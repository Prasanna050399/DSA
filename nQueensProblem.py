def canPlace(row, col, rows, cols, n):
    if row in rows:
        return False
    if col in cols:
        return False
    i = row
    j = col

##  diagonally up from left bottom to right top 
    while i>=0 and j<n:
        if i in rows and j in cols:
            return False
        i -= 1
        j += 1
##  diagonally down from left bottom to right top
    i = row
    j = col
    while i < n and j >= 0:
        if i in rows and j in cols:
            return False
        i += 1
        j -= 1
##  diagonally down from left top to right bottom
    i = row
    j = col
    while i < n and j < n:
        if i in rows and j in cols:
            return False
        i += 1
        j += 1
##  diagonally up from left top to right bottom
    i = row
    j = col
    while i >= 0 and j >= 0:
        if i in rows and j in cols:
            return False
        i -= 1
        j -= 1

    return True
        
def placeQueens(col, row, queensPos, rows, cols, n) :
    if canPlace(row, col, rows, cols, n):
        queenPos.append((row, col))
    else :

            
##        need to add logic if the placement is wrong till now need to replace the current queens

def nQueenProblem() :
    n = int(input())
    rows = dict()
    cols = dict()
    queensPos = list()
    for i in range(n):
        placeQueens(i, 0, queenPos, rows, cols, n)

    board = [[0]*n]*n
    for i in queenPos:
        board[i[0]][i[1]] = 1
    for i in board:
        print(i)


if __name__ == "__main__":
    nQueenProblem()
