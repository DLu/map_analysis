from bucket_queue import BucketQueue
from math import sqrt

class DataCell:
    def __init__(self, dist=INFINITY, sqdist=INT_MAX, obst=INVALID, voronoi=FREE, queueing = NOTQUEUED, needs_raise=False):
        self.dist = dist
        self.sqdist = sqdist
        self.obst = obst
        self.voronoi = voronoi
        self.queueing = queueing
        self.needs_raise = needs_raise
        
    def isOccupied(self, x, y):
        if obst==INVALID:
            return False
        else:
            return c.obst[0]==x and c.obst[1]==y
            
class DynamicVoronoi:
    def __init__(self, size_x, size_y, initial_map=None):
        self.size_x = size_x
        self.size_y = size_y
        self.last_obstacles = []
        self.remove_list = []
        self.add_list = []
        self.q = BucketQueue()
    
        self.data = []
        for x in range(size_x):
            self.data.append([])
            for y in range(size_y):
                self.data[-1].append(DataCell())
        
        self.grid_map = []
        if not initial_map:
            for x in range(size_x):
                self.grid_map.append( [0] * size_y )
        else:
            self.grid_map = initial_map
            for x in range(size_x):
                for y in range(size_y):
                    if self.grid_map[x][y]:
                        c = self.data[x][y]
                        if not c.is_occupied(x,y):
                            if self.is_surrounded(x,y):
                                c.obst = (x,y)
                                c.dist = 0
                                c.sqdist = 0
                                c.voronoi=occupied
                                c.queueing = fwProcessed
                            else:
                                self.setObstacle(x,y)
                                
    def get_neighbors(self, x, y):
        a = []
        for dx in [-1, 0, 1]:
            nx = x + dx
            if nx<=0 or nx >= self.size_x-1:
                continue
            for dy in [-1, 0, 1]:
                if dx==0 and dy==0:
                    continue
                ny = y + dy
                if ny<=0 or ny >= self.size_y-1:
                    continue
                a.append(nx, ny)
        return a
        
    def is_surrounded(self, x, y):
        for nx, ny in self.get_neighbors(x,y):
            if not self.grid_map[nx][ny]:
                return False
        return True         
    
    def occupy_cell(self, x, y):
        """add an obstacle at the specified cell coordinate"""
        self.grid_map[x][y] = 1
        self.setObstacle(x,y)

    def clear_cell(self, x, y):
        """remove an obstacle at the specified cell coordinate"""
        self.grid_map[x][y] = 0
        self.removeObstacle(x,y)
        
    def setObstacle(self, x, y):
        c = self.data[x][y]
        if c.isOccupied(x,y):
            return
        self.add_list.append( (x,y) )
        c.obst = (x,y)
        
    def removeObstacle(self, x, y):
        c = self.data[x][y]
        if not c.isOccupied(x,y):
            return
        self.remove_list.append((x,y))
        c.obst = INVALID
        c.queueing = QUEUED
        
        
    def exchange_obstacles(self, new_obstacles):
        """remove old dynamic obstacles and add the new ones"""
        for x,y in self.last_obstacles:
            if self.grid_map[x][y]:
                continue
            self.removeObstacles(x,y)
        self.last_obstacles = []
        
        for x,y in new_obstacles:
            if self.grid_map[x][y]:
                continue
            self.setObstacle(x,y)
            self.last_obstacles.append((x,y))

    
        

    def update(self, update_real_dist=True):
        """update distance map and Voronoi diagram to reflect the changes"""
        self.commit_and_colorize(update_real_dist)
        while not self.q.empty():
            x,y = self.q.pop()
            c = self.data[x][y]
            
            if c.queueing==fwProcessed:
                continue
                
            if c.needsRaise:
                # RAISE
                for nx, ny in self.get_neighbors(x,y):
                    nc = self.data[nx][ny]
                    if not (nc.obst != INVALID and not nc.needsRaise):
                        continue
                    nox, noy = nc.obst
                    tc = self.data[nox][noy]
                    if not tc.isOccupied(nox, noy):
                        self.q.push( nc.sqdist, (nx, ny) )
                        nc.queueing = fwQueued
                        nc.needsRaise = True
                        nc.obst = INVALID
                        if update_real_dist:
                            nc.dist = INFINITY
                        nc.sqdist = INT_MAX
                    else:
                        if nc.queueing != fwQueued:
                            self.q.push(nc.sqdist, (nx, ny))
                            nc.queueing = fwQueued
                c.needsRaise = False
                c.queueing = bwProcessed
            
            elif (c.obst != INVALID and self.data[ c.obst[0] ][ c.obst[1] ].isOccupied(c.obst[0],c.obst[1])):
                # LOWER
                c.queueing = fwProcessed;
                c.voronoi = occupied;

                for nx, ny in self.get_neighbors(x,y):
                    nc = self.data[nx][ny]
                    if(!nc.needsRaise) {
                        distx = nx - c.obst[0]
                        disty = ny - c.obst[1]
                        newSqDistance = distx*distx + disty*disty		
                        overwrite =  (newSqDistance < nc.sqdist)
                        if(!overwrite and newSqDistance==nc.sqdist): 
                            if (nc.obst == INVALID or not self.data[nc.obst[0]][self.obst[1]].isOccupied(nc.obst[0],nc.obst[1]):
                                overwrite = True
                        
                        if overwrite:
                            self.q.push(newSqDistance, (nx,ny))
                            nc.queueing = fwQueued
                            if update_real_dist:
                                nc.dist = sqrt(float(newSqDistance))
                            
                            nc.sqdist = newSqDistance;
                            nc.obstX = c.obstX;
                            nc.obstY = c.obstY;
                        else: 
                            self.checkVoro(x,y,nx,ny,c,nc);
                        
                        
  //! prune the Voronoi diagram
  void prune();
  
  //! returns the obstacle distance at the specified location
  float getDistance( int x, int y );
  //! returns whether the specified cell is part of the (pruned) Voronoi graph
  bool isVoronoi( int x, int y );
  //! checks whether the specficied location is occupied
  bool isOccupied(int x, int y);
  //! write the current distance map and voronoi diagram as ppm file
  void visualize(const char* filename="result.ppm");

  //! returns the horizontal size of the workspace/map
  unsigned int getSizeX() {return sizeX;}
  //! returns the vertical size of the workspace/map
  unsigned int getSizeY() {return sizeY;}



  typedef enum {voronoiKeep=-4, freeQueued = -3, voronoiRetry=-2, voronoiPrune=-1, free=0, occupied=1} State;
  typedef enum {fwNotQueued=1, fwQueued=2, fwProcessed=3, bwQueued=4, bwProcessed=1} QueueingState;
  typedef enum {invalidObstData = SHRT_MAX/2} ObstDataState;
  typedef enum {pruned, keep, retry} markerMatchResult;


  
  // methods
  inline void checkVoro(int x, int y, int nx, int ny, dataCell& c, dataCell& nc);
  void recheckVoro();
  void commitAndColorize(bool updateRealDist=true);
  inline void reviveVoroNeighbors(int &x, int &y);
  inline markerMatchResult markerMatch(int x, int y);

  // queues
  std::queue<INTPOINT> pruneQueue;


  // parameters
  int padding;
  double doubleThreshold;

  double sqrt2;

  //  dataCell** getData(){ return data; }
};


#endif

