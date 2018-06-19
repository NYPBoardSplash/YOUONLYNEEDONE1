import cv2
import numpy as np
import math
import sys

# define constants
MAX_THETA_DIFF = np.pi / 180 * 10
MAX_RHO_DIFF = 50

showDebugMessages = True

# ------------------------------------------------------------------------
# Class for containing the chess board's intersection lines
# ------------------------------------------------------------------------
def debugprint(s):
    if showDebugMessages:
        print (s);

# ------------------------------------------------------------------------
# Class for containing the chess board's intersection lines
# ------------------------------------------------------------------------
class ChessBoardLine:

    def __init__ (self, _rho, _theta):
        # make sure _rho > 0 for easy duplicate line detection
        if _rho < 0:
            _rho = -_rho
            _theta = _theta - np.pi

        self.rho = _rho
        self.theta = _theta
    
    def isNearAndParallel(self, line):   
        line_theta = line.theta
        line_rho = line.rho
        
        thetaDiff = abs(self.theta - line_theta)
        rhoDiff = abs(self.rho - line_rho)
        if (thetaDiff < MAX_THETA_DIFF and
            rhoDiff < MAX_RHO_DIFF):
            return True

    def getRho(self):
        return self.rho

# ------------------------------------------------------------------------
# Class for containing the chess information
# ------------------------------------------------------------------------
class Chess:

    # RGB colours for the pieces' black / red / cream
    # (we should use k-means to train this but this will do for now...)
    pieceColors = [
        [  90, 120, 150 ],        # cream
        [  20,  20, 120 ],        # red
        [  20,  30, 50 ]]        # black

    def __init__(self):
        self.sift = cv2.xfeatures2d.SIFT_create()
        self.matcher = cv2.BFMatcher()

        # load up the individual chess piece image and compute the SIFT descriptors
        #
        self.pieceSiftDescriptors = []
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('b').computeFromFile(self.sift, 'training/chars/chess-advisor1.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('b').computeFromFile(self.sift, 'training/chars/chess-advisor2.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('c').computeFromFile(self.sift, 'training/chars/chess-cannon.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('r').computeFromFile(self.sift, 'training/chars/chess-chariot.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('k').computeFromFile(self.sift, 'training/chars/chess-general1.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('k').computeFromFile(self.sift, 'training/chars/chess-general2.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('a').computeFromFile(self.sift, 'training/chars/chess-guard.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('n').computeFromFile(self.sift, 'training/chars/chess-horse.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('p').computeFromFile(self.sift, 'training/chars/chess-pawn1.png'))
        self.pieceSiftDescriptors.append(ChessPieceDescriptor('p').computeFromFile(self.sift, 'training/chars/chess-pawn2.png'))
        
    # find the squared-distance between two different colours
    # 
    def findDistanceBetweenColours(self, c1, c2):
        return (c1[0]-c2[0])*(c1[0]-c2[0]) + (c1[1]-c2[1])*(c1[1]-c2[1]) + (c1[2]-c2[2])*(c1[2]-c2[2])

    # find the index of the one of the 3 colours (cread, red, black) from the colour c
    #
    def findClosestDistanceColor(self, c):
        nearestDist = 999999999
        nearestColor = 0
        for i in range(0, 3):
            dist = self.findDistanceBetweenColours(c, self.pieceColors[i])
            #debugprint ("  %d " % (dist))
            if dist < nearestDist:
                nearestColor = i
                nearestDist = dist
        return nearestColor

    # Given an entire image, posterize and then count the number of cream, red, black pixels
    # A piece is considered black if there are more black than red pixels.
    # A piece is considered red if there are more red than black pixels.
    def matchPieceColor(self, pieceImg):
        binCount = [0,0,0]    
        #finalColorImg = pieceImg.copy()
        for y in range(0, pieceImg.shape[0]):
            for x in range(0, pieceImg.shape[1]):
                #debugprint (pieceImg[y][x])
                color = self.findClosestDistanceColor(pieceImg[y][x])
                #finalColorImg[y][x] = self.pieceColors[color]
                binCount[color] = binCount[color] + 1
        
        # count the number of percentage of the number of pixels 
        # of the cream / red / black colours
        #
        #pixelCount = pieceImg.shape[0] * pieceImg.shape[1]
        #for i in range(0, 3):
        #    binCount[i] = binCount[i] * 100 / pixelCount
        
        if (binCount[2] > binCount[1]):     # if % of black is more than % of red pixels
            return 2 # black
        else:
            return 1 # red    


    # Given two non-parallel lines, find their intersection point.
    # This is used to find the intersection points between the horizontal and 
    # vertical lines of our chessboard.
    #
    def findIntersectionPoint(self, line1, line2):
        ct1 = math.cos(line1.theta)     # matrix element a
        st1 = math.sin(line1.theta)     # b
        ct2 = math.cos(line2.theta)     # c
        st2 = math.sin(line2.theta)     # d
        d = ct1*st2 - st1*ct2          # determinative (rearranged matrix for inverse)
        if d != 0.0:   
            return ( ((st2 * line1.rho - st1 * line2.rho)/d), 
                    ((-ct2 * line1.rho + ct1 * line2.rho)/d) )
        else:
            debugprint("Error finding intersection!!!!")
            return None

    # Draws the detected lines on the output
    #
    def drawLine(self, line, chessboard_output, color):
        a = np.cos(line.theta)
        b = np.sin(line.theta)
        x0 = a * line.rho
        y0 = b * line.rho
        x1 = int(x0 + 2000*(-b))
        y1 = int(y0 + 2000*(a))
        x2 = int(x0 - 2000*(-b))
        y2 = int(y0 - 2000*(a))

        cv2.line(chessboard_output,(x1,y1),(x2,y2),(255,0,0),2)
        

    # let's detect the lines and insert into our array
    # this insertLine detects nearby duplicate parallel lines and discards them
    #
    def detectLines(self, chessboard_colour, chessboard_gray, chessboard_output):
        chessboard_edges = cv2.Canny(chessboard_gray,50,150,apertureSize = 3)
        lines = cv2.HoughLines(chessboard_edges,1,np.pi / 180, 180)
        #debugprint ("Lines found : %d" % (len(lines)))

        self.boardLines = []
        self.verticalLines = []
        self.horizontalLines = []
        for i in range(0, len(lines)):
            line = ChessBoardLine(lines[i][0][0], lines[i][0][1])
            
            # test if this line is close to an existing line with about the
            # same angle.
            #
            isUniqueLine = True
            for j in range(0, len(self.boardLines)):
                if line.isNearAndParallel(self.boardLines[j]):
                    isUniqueLine = False
            
            if isUniqueLine:
                #self.drawLine(line, chessboard_output, (0, 255, 0))
                self.boardLines.append(line)
                rho = line.rho
                theta = line.theta

        # We extract out the vertical and horizontal lines and sort them by
        # their rho values. 
        # 
        for i in range(0, len(self.boardLines)):
            # Horizontal lines (roughly about 90 degrees)
            if (self.boardLines[i].theta >= 70.0 * np.pi / 180 and 
                self.boardLines[i].theta <= 110.0 * np.pi / 180):
                self.horizontalLines.append(self.boardLines[i])

            # Vertical lines (roughly about 0 degrees)
            if (self.boardLines[i].theta >= -20.0 * np.pi / 180 and 
                self.boardLines[i].theta <= 20.0 * np.pi / 180):
                self.verticalLines.append(self.boardLines[i])

        # Let's just assume that the camera takes a picture top-down, but the general pieces are on
        # the left and right side of the board.
        #
        # Furthermore we will assume that the robot player is on the left side of the camera,
        # the human player is on the right side of the camera
        #
        # (This also means that the camera is on the right side of the robot player)
        #
        #                  +----+
        #            Robot |    | Human
        #                  +----+
        #
        self.verticalLines.sort(key=ChessBoardLine.getRho)    
        self.horizontalLines.sort(key=ChessBoardLine.getRho)    

        for i in range(0, len(self.verticalLines)):
            debugprint("Vertical Line:   %f %f" % (self.verticalLines[i].rho, self.verticalLines[i].theta))
        for i in range(0, len(self.horizontalLines)):
            debugprint("Horizontal Line: %f %f" % (self.horizontalLines[i].rho, self.horizontalLines[i].theta))

        # In case the edges of the chess board paper are detected, we have to find a way
        # to ignore those lines. In general the actual black lines on the chess board 
        # are generally equally spaced apart, so we can use the spacing in the lines near the 
        # middle of the board as benchmark.
        #
        # do vertical lines first
        #
        if (len(self.verticalLines) > 10):

            ratio = (self.verticalLines[1].rho - self.verticalLines[0].rho) / (self.verticalLines[2].rho - self.verticalLines[1].rho)
            if (ratio > 1.3 or ratio < 0.7):
                self.verticalLines.remove(self.verticalLines[0])

            n = len(self.verticalLines) - 1
            ratio = (self.verticalLines[n].rho - self.verticalLines[n - 1].rho) / (self.verticalLines[n - 1].rho - self.verticalLines[n - 2].rho)
            if (ratio > 1.3 or ratio < 0.7):
                self.verticalLines.remove(self.verticalLines[n])

        # then do horizontal lines
        if (len(self.horizontalLines) > 9):

            ratio = (self.horizontalLines[1].rho - self.horizontalLines[0].rho) / (self.horizontalLines[2].rho - self.horizontalLines[1].rho)
            if (ratio > 1.3 or ratio < 0.7):
                self.horizontalLines.remove(self.horizontalLines[0])

            n = len(self.horizontalLines) - 1
            ratio = (self.horizontalLines[n].rho - self.horizontalLines[n - 1].rho) / (self.horizontalLines[n - 1].rho - self.horizontalLines[n - 2].rho)
            if (ratio > 1.3 or ratio < 0.7):
                self.horizontalLines.remove(self.horizontalLines[n])

        # just do some sanity check on the number of lines found
        #
        if (len(self.horizontalLines) != 9):
            debugprint ("ERROR: Horizontal lines count (%d) not equals 9!" % (len(self.horizontalLines)))
        if (len(self.verticalLines) != 10):
            debugprint ("ERROR: Vertical lines count (%d) not equals 10!" % (len(self.verticalLines)))

        # Then let's find the intersection points between all vertical and horizontal lines
        #
        self.intersectionPoints = []        
        for h in range(0, 9):
            self.intersectionPoints.append([
                [0,0], [0,0], [0,0], [0,0], [0,0],   
                [0,0], [0,0], [0,0], [0,0], [0,0]])
            
        for h in range(0, len(self.horizontalLines)):
            for v in range(0, len(self.verticalLines)):
                point = self.findIntersectionPoint(self.horizontalLines[h], self.verticalLines[v])
                if point is not None and h < 9 and v < 10:
                    self.intersectionPoints[h][v] = point
                    debugprint ("Point %d,%d = %f,%f" % (h,v,point[0],point[1]))
        
        # Finally, we draw all the detected horizontal + vertical lines
        for i in range(0, len(self.verticalLines)):
            self.drawLine(self.verticalLines[i], chessboard_output, (255, 0, 0))
        for i in range(0, len(self.horizontalLines)):
            self.drawLine(self.horizontalLines[i], chessboard_output, (255, 0, 0))
                   

    # Given a piece descriptor, find the best matching piece
    #
    def findBestChessPieceDescriptor(self, unknownPieceDescriptor):
        maxScore = 0
        maxScorePieceId = ""
        for i in range(0, len(self.pieceSiftDescriptors)):
            score = self.pieceSiftDescriptors[i].match(self.matcher, unknownPieceDescriptor)
            debugprint ("  matching: %s %d" % (self.pieceSiftDescriptors[i].id, score))
            if score > maxScore:
                maxScore = score
                maxScorePieceId = self.pieceSiftDescriptors[i].id
        
        return maxScorePieceId

    
    # find the board coordinates given a chess piece's x, y, radius on the image.
    # This function will return the h, v coordinate of the board
    #
    def findBoardPosition(self, x, y, r):
        for h in range(0, 9):
            for v in range(0, 10):
                ix = self.intersectionPoints[h][v][0]               
                iy = self.intersectionPoints[h][v][1]               
                dist = math.sqrt( (x-ix)*(x-ix) + (y-iy)*(y-iy) )
                if dist <= r:
                    return (h,v)
        return None


    # Using the chessboard passed in from the caller, detect all the pieces
    # and generate the FEN position
    #
    def detectPiecesAndColours(self, chessboard_color, chess_output_filename):
        
        # declares the board position array as boardPosition[9][10]
        # (9 horizontal positions, 10 vertical positions on the grid)
        # 
        boardPosition = []
        for i in range(0, 9):
            boardPosition.append([" ", " ", " ", " ", " ", " ", " ", " ", " ", " "])
        
        chessboard_output = chessboard_color.copy()
        chessboard_blur = cv2.medianBlur(chessboard_color, 5)
        chessboard_blurgray = cv2.cvtColor(chessboard_blur,cv2.COLOR_BGR2GRAY)
        chessboard_gray = cv2.cvtColor(chessboard_color,cv2.COLOR_BGR2GRAY)
        height, width = chessboard_output.shape[:2]

        self.detectLines(chessboard_color, chessboard_gray, chessboard_output)

        # let's detect circles
        #
        circles = cv2.HoughCircles(chessboard_blurgray,cv2.HOUGH_GRADIENT,1,40,param1=50,param2=30,minRadius=30,maxRadius=50)
        circles = np.uint16(np.around(circles))

        count = 0
        for i in circles[0,:]:
            cx = i[0]
            cy = i[1]
            radius = i[2]

            # draw the outer circle
            cv2.circle(chessboard_output,(cx,cy),radius,(0,255,0),2)

            # draw the center of the circle
            cv2.circle(chessboard_output,(cx,cy),2,(0,0,255),3)

            # extract the chess piece based on the detected circle
            expanded_radius = radius + 10
            x1 = cx - expanded_radius 
            x2 = cx + expanded_radius 
            y1 = cy - expanded_radius
            y2 = cy + expanded_radius
            if x1 < 0:
                x1 = 0
            if x2 >= chessboard_color.shape[1]:
                x2 = chessboard_color.shape[1] - 1;
            if y1 < 0:
                y1 = 0
            if y2 >= chessboard_color.shape[0]:
                y2 = chessboard_color.shape[0] - 1;
            
            chesspiece_color = chessboard_color[y1 : y2, x1 : x2]
            if radius > 10:
                radius -= 10
            chesspiece_inner_color = chessboard_color[cy - radius : cy + radius,cx - radius : cx + radius]

            debugprint (chesspiece_color.shape)
            if chesspiece_color.shape[0] > 0 and chesspiece_color.shape[1] > 0:
                # find the best matching SIFT descriptor and
                # thus determine the chess piece's name
                #
                unknownPieceDescriptor = ChessPieceDescriptor('').computeFromImage(self.sift, chesspiece_color)
                debugprint ("circle #%d" % (count))
                bestMatch = self.findBestChessPieceDescriptor(unknownPieceDescriptor)

                # find the best matching color in RGB space
                # now we use chesspiece_inner_color so that we can "crop"
                # out the border, in case the chess board's black lines are
                # captured in the circle
                #
                bestColor = self.matchPieceColor(chesspiece_inner_color)
                if bestColor == 1:
                    bestColorString = "R"
                    bestColorBGR = (0,255,255)
                    bestMatch = bestMatch.upper()       # red pieces are upper case
                else:
                    bestColorString = "B"
                    bestColorBGR = (0,0,0)              
                    bestMatch = bestMatch.lower()       # black pieces are lower case

                # Since we have the detected circle's position, see if it
                # lines up with one of the intersection points on our chess
                # board. 
                #
                pos = self.findBoardPosition(cx, cy, radius + 25)
                
                if pos is not None:
                    boardPosition[pos[0]][pos[1]] = bestMatch
                    debugprint ('best match %d:%s @ %d,%d' % (count, bestMatch, pos[0], pos[1]))

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(chessboard_output, '%d:%s' % (count, bestMatch), 
                        (cx - radius,cy + radius + 25), font, 0.8, bestColorBGR, 2, cv2.LINE_AA)
                else:
                    debugprint ('best match %d:%s @ no position' % (count, bestMatch))

            count = count + 1

        # Save our output image for debugging purposes.
        #
        chessboard_output_small = cv2.resize(chessboard_output,(int(width/2), int(height/2)), interpolation = cv2.INTER_CUBIC)
        cv2.imwrite(chess_output_filename, chessboard_output_small)

        # Let's print out final board position to our debug screen
        #
        for h in range(0, 9):
            debugprint (boardPosition[h])

        # generate the FEN position as required by the UCCI protocol
        #
        fen = ""
        for vt in range(0, 10):
            v = 9 - vt
            emptyCounter = 0
            for h in range(0, 9):
                piece = boardPosition[h][v]
                if piece == " ":
                    emptyCounter = emptyCounter + 1
                else:
                    if emptyCounter > 0:
                        fen = fen + ("%d" % emptyCounter)
                        emptyCounter = 0
                    fen = fen + piece
            
            if emptyCounter > 0:
                fen = fen + ("%d" % emptyCounter)
                emptyCounter = 0

            if vt < 9:
                fen = fen + "/"
        
        debugprint ("Generated FEN: " + fen)
        return fen

    # Loads the chess board image and generates the FEN board position.
    # 
    def loadImageAndDetectPiecesAndColours(self, chess_input_file, chess_output_file):
        # load the input image
        #
        chessboard_color = cv2.imread(chess_input_file)
        debugprint (chessboard_color.shape)

        # Force the captured image to be sized to 1600 width, since that's the
        # dimension we've developed this recognizer for.
        #
        if chessboard_color.shape[1] != 1600:
            ratio = 1600.0 / chessboard_color.shape[1] 
            chessboard_color = cv2.resize(chessboard_color, 
                (int(chessboard_color.shape[1] * ratio), int(chessboard_color.shape[0] * ratio)), 
                interpolation = cv2.INTER_CUBIC)

        # Performs computer vision and recognizes the board
        #
        chess = Chess()
        fen = chess.detectPiecesAndColours(chessboard_color, chess_output_file)

        return fen



# ------------------------------------------------------------------------
# Class for containing the keypoints
# and descriptors for a chess piece.
# ------------------------------------------------------------------------
class ChessPieceDescriptor:
    id = ""
    kp = []
    desc = []

    def __init__(self, _id):
        self.id = _id

    def computeFromImage(self, sift, img):
        self.kp, self.desc = sift.detectAndCompute(img, None)
        #img_gray = cv2.drawKeypoints(img, self.kp, None)
        return self

    def computeFromFile(self, sift, filename):
        img = cv2.imread(filename,0) # trainImage
        #img_gray = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
        self.computeFromImage(sift, img)
        return self

    def match(self, matcher, piece) : 
        matches = matcher.knnMatch(self.desc, piece.desc, k=2)

        # Apply ratio test
        good_count = 0
        for m,n in matches:
            if m.distance < 0.75*n.distance:
                good_count = good_count + 1

        return good_count * 100 / len(self.desc)


# ------------------------------------------------------------------------
# A class for performing unit testing.
# ------------------------------------------------------------------------
class ChessTester:
    def testAndAssert(self, chess_input_file, chess_output_file, expected_fen):

        # Loads, recognizes the pieces and generates the FEN
        #
        self.chess = None
        self.chess = Chess()
        self.fen = self.chess.loadImageAndDetectPiecesAndColours(chess_input_file, chess_output_file)
        
        # Asserts and print results to the screen
        #
        if self.fen == expected_fen:
            print ('%s: FEN test passed' % chess_input_file)
        else:
            print ('%s: FEN test failed.\n  Expected: %s\n  Actual:   %s' % (chess_input_file, expected_fen, self.fen))
        
    
# ------------------------------------------------------------------------
# To run this program:
#
# python recognizeboard.py input.jpg output.jpg b/w 
# where:
#   input.jpg
#   - The input image file
#
#   output.jpg
#   - The output image file
#
#   b/w
#   - indicates the color of the player that the AI chess program should move. 
#
# This python program accepts input of:
#   - input.jpg 
#     (the captured image of the chess board from top-down position)
#
# It outputs:
#   - output.jpg
#     (recognized lines and pieces draw on top of the original image)
#
#   - ucci_input.txt
#     (commands, including the recognized board's FEN position that 
#      can be piped into the AI chess program)
# ------------------------------------------------------------------------

# Determine whose move from the command line
#
if len(sys.argv) < 2:
    print ("Usage: python recognizeboard.py [command] [input.jpg] [output.jpg] [uccioutput.txt] [b/w] [easy/adv]")
    sys.exit(0)

command = sys.argv[1]

if command == 'run':
    # run the recognition and generates the UCCI file
    #
    showDebugMessages = True

    if len(sys.argv) != 7:
        print ("Usage: python recognizeboard.py [command] [input.jpg] [output.jpg] [uccioutput.txt] [b/w] [easy/adv]")
        exit

    chess_input_file = sys.argv[2]
    chess_output_file = sys.argv[3]
    chess_ucci_file = sys.argv[4]
    whoseMove = 'w'
    if sys.argv[5] == 'b':
        whoseMove = 'b'
    rank='easy'
    if sys.argv[6]=='adv':
        rank='adv'


    # Performs computer vision and recognizes the board
    #
    chess = Chess()
    fen = chess.loadImageAndDetectPiecesAndColours(chess_input_file, chess_output_file)

    if rank=='adv':
        # if the rank is easy , we will generate this txt file
        #########################################################
        # Writes our UCCI command to the file. We can simply just pipe this file
        # into our chess program to generate the best move.
        #
        file = open(chess_ucci_file,"w+")
        file.write("ucci\n") 
        file.write("position fen " + fen + " " + whoseMove + " - - 0 1\n")       
        file.write("go time 20000\n")
        file.close()
    else:
        #else we generate this txt file and set the randomness will set to huge
        #########################################################
        # Writes our UCCI command to the file. We can simply just pipe this file
        # into our chess program to generate the best move.
        #
        file = open(chess_ucci_file,"w+")
        file.write("ucci\n") 
        file.write("setoption randomness huge\n")  
        file.write("position fen " + fen + " " + whoseMove + " - - 0 1\n")    
        file.write("go time 10000\n")
        file.close()
   
    redMark=0
    blackMark=0
    ai=0
    bi=0
    Message="You have "
    for li in fen:
        if li =="r":
           
            ai=ai+1
            blackMark=blackMark+9
            #Message=Message+" "+ str(ai) +" Assitance "
        if li =="n":
            bi=bi+1
            blackMark=blackMark+7
            #Message=Message+" "+ str(bi) +" Bishop "
        if li== "b":
            blackMark=blackMark+3
        if li == "a":
            blackMark=blackMark+3
        if li == "k":
            blackMark=blackMark+2
        if li=="c":
            blackMark=blackMark+7
        if li=="p":
            blackMark=blackMark+1
        if li =="P":
           redMark=redMark+1
        if li =="C":
            redMark=redMark+7
        if li =="R":
            redMark=redMark+9
        if li =="N":
            redMark=redMark+7
        if li=="B":
            redMark=redMark+3
        if li =="A":
            redMark=redMark+3
        if li =="K":
            redMark=redMark+1

    


if command == 'test':
    print ("Running test cases...")

    # Runs some tests against the test images
    #
    showDebugMessages = False

    test = ChessTester()
    test.testAndAssert('chess_input_0.jpeg', 'chess_output_0.jpeg', 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR')
    test.testAndAssert('chess_input_1.jpeg', 'chess_output_1.jpeg', 'c1BNK4/4A4/2n6/2P1p1n1P/9/4R4/p8/5a3/5k3/9')
    test.testAndAssert('chess_input_2.jpeg', 'chess_output_2.jpeg', '2bakab1r/3r5/2n1c1nc1/p1p1p1p1p/9/2P4R1/P3P1P1P/1CN1C1N2/9/R1BAKAB2')
    test.testAndAssert('chess_input_3.jpeg', 'chess_output_3.jpeg', 'c1BNK4/4A4/2n6/2P5P/4p4/4Cn3/p1p6/4ca3/5k3/2R6')
    test.testAndAssert('chess_input_4.jpeg', 'chess_output_4.jpeg', '2BAKA3/9/2N1p4/P1P5P/9/4pn3/p1p6/c1n1c3R/4a4/2bak1C2')
    test.testAndAssert('chess_input_large_5.jpeg', 'chess_output_large_5.jpeg', '2B1K4/4A4/2N6/P1P5P/4p4/5n3/p1p1n4/c3ca3/4k4/2bC4R')

    print ("Done.")