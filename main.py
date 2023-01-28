from typing import List


class World:
    WIDTH = 10
    HEIGHT = 20

    board = set() # set of points that exist in the world
    
    def __init__(self) -> None:
        pass
    
    def lineIsComplete(self, y: int) -> bool:
        for x in range(self.WIDTH):
            if (x,y) not in self.board:
                return False
            
        return True
    
    def getDisplacementsPerLine(self, deleted_lines : List[int]) -> List[int]:
        result = []
        for i in range(len(deleted_lines)):
            cur_y = deleted_lines[i]
            prev_y = deleted_lines[i-1] if i > 0 else -1
            for _ in range(prev_y + 1, cur_y):
                result.append(i)
            result.append(0) # the deleted line has no displacement
            
        return result
        
    def deleteLine(self, y : int) -> None:
        for x in range(self.WIDTH):
            if (x,y) in self.board:
                self.board.remove((x,y))

    
    def resolveCompleteLines(self) -> int:
        """Check the entire state of the board and do the following 
            1. Delete any complete lines
            2. Translate other lines downward
            
            Returns the number of deleted lines
        """
        deleted_lines = set() # set of y coordinates
        for y in range(self.HEIGHT):
            if self.lineIsComplete(y):
                deleted_lines.add(y)
            
        for y in deleted_lines:
            self.deleteLine(y)
        
        displacements_per_line = self.getDisplacementsPerLine(deleted_lines)
        
        for y, displacement in enumerate(displacements_per_line):
            for x in range(self.WIDTH):
                if (x,y) in self.board:
                    self.board.remove((x,y))
                    self.board.add((x,y-displacement))
                    
        return len(deleted_lines)
    
    def addPiece(self, state : set) -> None:
        """Add a piece to the state of the static world"""
        for (x,y) in state:
            self.board.add((x,y))
        
    def checkIfCoordInState(self, x: int, y: int) -> bool:
        return (x,y) in self.board
    
import random
class Piece:
    def adjacentPositions(self, x :int, y : int) -> bool:
        adjacent_positions = {(x-1,y),(x+1,y),(x,y-1),(x,y+1)}
        return adjacent_positions
    
    def boundaryOfState(self) -> set:
        adjacent_positions = set()
        for (x,y) in self.state:
            adjacent_to_block = self.adjacentPositions(x,y)
            adjacent_positions = adjacent_positions.union(adjacent_to_block - self.state)
            
        return adjacent_positions
        
    def addCubeToState(self) -> None:
        boundary = self.boundaryOfState()
        self.state.add(random.choice(tuple(boundary)))
 
    def initializeState(self) -> None:
        x_start = round(1 + random.random() * 8)
        y_start = 16
        self.state.add((x_start, y_start))
        for i in range(3): # 4 squares in a tromino
            self.addCubeToState()
    
    def __init__(self) -> None:
        self.state = set()
        self.initializeState() # TODO how to randomly generate the state as one of the trominos?
        
    def rotate(self) -> None:
        pass # TODO
    
    def displace(self, dx: int, dy: int, world: World) -> bool:
        """N.B. positive dx means moving right, positive dy means moving up

            Return True if we collide with a piece below or the bottom of the world
            
            N.B. Collisions below are treated differently than collisions to the left or right
            
            Collisions below are "sticky" i.e. the piece gets stuck to whatever is below, and is no longer moveable.
            Meanwhile, a collision to the left or right is not sticky! And we can still move the piece.
        """
        assert (dx == 0) != (dy == 0) # can only displace either horizontally or vertically
        
        new_state = set()
        for (x,y) in self.state:
            new_coord = (x+dx,y+dy)
            if new_coord in world.board or new_coord[0] >= world.WIDTH or new_coord[0] < 0 or new_coord[1] < 0:
                if dy != 0:
                    return True # collision below!
                else:
                    return False # do not update state of the piece when colliding horizontally.
            new_state.add(new_coord)

        self.state = new_state
        

def render(world: World, piece : Piece) -> None:
    combined_state = world.board.union(piece.state)
    lines = []
    for y in range(world.HEIGHT):
        line = "|"
        for x in range(world.WIDTH):
            line += "*" if (x,y) in combined_state else " "
        line += "|"
        lines.append(line)
        
    for line in reversed(lines):
        print(line)
    
    print("+" * (2 + world.WIDTH))
            


def main() -> None:
    world = World()
    score = 0
    
    while True:
        # current falling piece
        piece = Piece()
        
        while True:
            render(world, piece)
            # player callbacks
            key = input("Enter a direction: ")
            if key == "L":
                piece.displace(-1, 0, world)
            if key == "R":
                piece.displace(1,0, world)
            
            collision_below = piece.displace(0,-1, world) # piece is always moving down whether we like it or not!
            if collision_below:
                world.addPiece(piece.state) # piece gets stuck
                # scoring/line crunching
                num_deleted_lines = world.resolveCompleteLines()
                score += num_deleted_lines
                
                break # generate new piece
    

if __name__ == "__main__":
    main()