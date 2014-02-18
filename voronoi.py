from bucket_queue import BucketQueue
from math import sqrt
import sys

INFINITY = float('inf')
INT_MAX = sys.maxint

class State:
    KEEP=-4
    FREE_QUEUED = -3
    RETRY=-2
    PRUNE=-1
    FREE=0
    OCCUPIED=1
    
class QState:
    FW_NOT_QUEUED = 1
    FW_QUEUED=2
    FW_PROCESSED=3
    BW_QUEUED=4
    BW_PROCESSED=1
    
class MatchResult:
    PRUNED = 0
    KEEP = 1
    RETRY = 2

class DataCell:
    def __init__(self, dist=INFINITY, sqdist=INT_MAX, obst=None, voronoi=State.FREE, queueing = QState.FW_NOT_QUEUED, needs_raise=False):
        self.dist = dist
        self.sqdist = sqdist
        self.obst = obst
        self.voronoi = voronoi
        self.queueing = queueing
        self.needs_raise = needs_raise
        
    def isOccupied(self, x, y):
        if obst==None:
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
        self.prune_q = []
    
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
                                c.queueing = QState.FW_PROCESSED
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
        c.obst = None
        c.queueing = QState.BW_PROCESSED
        
        
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

    
    def check_obstacle_occupation(self, cell):
        if cell.obst == None:
            return False
        x, y = cell.obst
        c2 = self.data[x][y]
        return cell.isOccupied(x,y)        

    def update(self, update_real_dist=True):
        """update distance map and Voronoi diagram to reflect the changes"""
        self.commit_and_colorize(update_real_dist)
        while not self.q.empty():
            x,y = self.q.pop()
            c = self.data[x][y]
            
            if c.queueing==QState.FW_PROCESSED:
                continue
                
            if c.needsRaise:
                # RAISE
                for nx, ny in self.get_neighbors(x,y):
                    nc = self.data[nx][ny]
                    if not (nc.obst is not None and not nc.needsRaise):
                        continue
                    nox, noy = nc.obst
                    tc = self.data[nox][noy]
                    if not tc.isOccupied(nox, noy):
                        self.q.push( nc.sqdist, (nx, ny) )
                        nc.queueing = QState.FW_QUEUED
                        nc.needsRaise = True
                        nc.obst = None
                        if update_real_dist:
                            nc.dist = INFINITY
                        nc.sqdist = INT_MAX
                    else:
                        if nc.queueing != QState.FW_QUEUED:
                            self.q.push(nc.sqdist, (nx, ny))
                            nc.queueing = QState.FW_QUEUED
                c.needsRaise = False
                c.queueing = QState.BW_PROCESSED
            
            elif self.check_obstacle_occupation(c):
                # LOWER
                c.queueing = QState.FW_PROCESSED
                c.voronoi = occupied;

                for nx, ny in self.get_neighbors(x,y):
                    nc = self.data[nx][ny]
                    if not nc.needsRaise:
                        distx = nx - c.obst[0]
                        disty = ny - c.obst[1]
                        newSqDistance = distx*distx + disty*disty		
                        overwrite =  (newSqDistance < nc.sqdist)
                        if(not overwrite and newSqDistance==nc.sqdist): 
                            if not self.check_obstacle_occupation(nc):
                                overwrite = True
                        
                        if overwrite:
                            self.q.push(newSqDistance, (nx,ny))
                            nc.queueing = QState.FW_QUEUED
                            if update_real_dist:
                                nc.dist = sqrt(float(newSqDistance))
                            
                            nc.sqdist = newSqDistance;
                            nc.obst[0] = c.obst[0];
                            nc.obst[1] = c.obst[1];
                        else: 
                            self.checkVoro(x,y,nx,ny,c,nc);
                        
    def prune(self):          
        """prune the Voronoi diagram"""
        # filler
        while(len(self.prune_q)>0):
            x,y = self.prune_q.pop(0)

            if self.data[x][y].voronoi==occupied: 
                continue
                
            if self.data[x][y].voronoi==State.FREE_QUEUED:
                continue

            self.data[x][y].voronoi = State.FREE_QUEUED
            
            self.q.push(self.data[x][y].sqdist, (x,y));

            # tl t tr
            #  l c r
            #  bl b br 

            tr = self.data[x+1][y+1]
            tl = self.data[x-1][y+1]
            br = self.data[x+1][y-1]
            bl = self.data[x-1][y-1]
            r = self.data[x+1][y]
            l = self.data[x-1][y]
            t = self.data[x][y+1]
            b = self.data[x][y-1]

            if x+2<self.size_x and r.voronoi==occupied:
                # fill to the right
                if tr.voronoi!=occupied and br.voronoi!=occupied and self.data[x+2][y].voronoi!=occupied:
                    r.voronoi = State.FREE_QUEUED
                    self.q.push(r.sqdist, (x+1,y))
            if x-2>=0 and l.voronoi==occupied: 
                # fill to the left
                if tl.voronoi!=occupied and bl.voronoi!=occupied and self.data[x-2][y].voronoi!=occupied:
                    l.voronoi = State.FREE_QUEUED
                    self.q.push(l.sqdist, (x-1,y))
            if y+2<sizeY and t.voronoi==occupied: 
                # fill to the top
                if tr.voronoi!=occupied and tl.voronoi!=occupied and self.data[x][y+2].voronoi!=occupied:
                    t.voronoi = State.FREE_QUEUED
                    self.q.push(t.sqdist, (x,y+1))
            if y-2>=0 and b.voronoi==occupied: 
                # fill to the bottom
                if br.voronoi!=occupied and bl.voronoi!=occupied and self.data[x][y-2].voronoi!=occupied:
                    b.voronoi = State.FREE_QUEUED;
                    self.q.push(b.sqdist, INTPOINT(x,y-1));
                    data[x][y-1] = b;


        while not self.q.empty():
            x,y = self.q.pop()
            c = self.data[x][y]
            v = c.voronoi
            
            if v!=State.FREE_QUEUED and v!=State.RETRY: # or v>free or v==voronoiPrune or v==State.KEEP) {
                #      assert(v!=retry);
                continue
            
            r = markerMatch(x,y)
            if r==MatchResult.PRUNED:
                c.voronoi = State.PRUNE
            elif r==MatchResult.KEEP:
                c.voronoi = State.KEEP;
            else: # r==retry
                c.voronoi = State.RETRY
                #      printf("RETRY %d %d\n", x, sizeY-1-y);
                self.prune_q.append((x,y));

            if self.q.empty():
                while len(self.prune_q)>0:
                    x,y = self.prune_q.pop(0)
                    self.q.push( self.data[x][y].sqdist, (x,y))
          #  printf("match: %d\nnomat: %d\n", matchCount, noMatchCount);

  
    def getDistance(self, x, y):
        """returns the obstacle distance at the specified location"""
        if (x>0) and (x<self.size_x) and (y>0) and (y<self.size_y):
            return self.data[x][y].dist
        return -INFINITY


    def isVoronoi(self, x, y):
        """returns whether the specified cell is part of the (pruned) Voronoi graph"""
        c = self.data[x][y]
        return c.voronoi==State.FREE or c.voronoi==State.KEEP

    def isOccupied(self, x, y):
        """whether the specficied location is occupied"""
        c = self.data[x][y]
        return c.obst[0]==x and c.obst[1]==y
        
    def visualize(self, filename="result.ppm"):
        """ write the current distance map and voronoi diagram as ppm file"""
        None
        
    def checkVoro(self, x, y, nx, ny, c, nc):
        if not ((c.sqdist>1 or nc.sqdist>1) and nc.obst is not None):
            return
        if not (abs(c.obst[0]-nc.obst[0]) > 1 or abs(c.obst[1]-nc.obst[1]) > 1):
            return
    
        #compute dist from x,y to obstacle of nx,ny	 
        dxy_x = x-nc.obst[0];
        dxy_y = y-nc.obst[1];
        sqdxy = dxy_x*dxy_x + dxy_y*dxy_y;
        stability_xy = sqdxy - c.sqdist;
        if sqdxy - c.sqdist<0:
            return;

        #compute dist from nx,ny to obstacle of x,y
        dnxy_x = nx - c.obst[0];
        dnxy_y = ny - c.obst[1];
        sqdnxy = dnxy_x*dnxy_x + dnxy_y*dnxy_y;
        stability_nxy = sqdnxy - nc.sqdist;
        if sqdnxy - nc.sqdist <0:
            return

        #which cell is added to the Voronoi diagram?
        if stability_xy <= stability_nxy and c.sqdist>2:
            if c.voronoi != State.FREE:
                c.voronoi = State.FREE
                self.reviveVoroNeighbors(x,y)
                self.prune_q.append((x,y))
        if stability_nxy <= stability_xy and nc.sqdist>2:
            if nc.voronoi != State.FREE:
                nc.voronoi = State.FREE;
                self.reviveVoroNeighbors(nx,ny)
                self.prune_q.append((nx,ny))


    def reviveVoroNeighbors(self, x, y):
        for nx, ny in self.getNeighbors(x,y):
            nc = self.data[nx][ny]
            if nc.sqdist != INT_MAX and not nc.needsRaise and (nc.voronoi == State.KEEP or nc.voronoi == State.PRUNE):
                nc.voronoi = State.FREE
                self.prune_q.append((nx,ny))


    def commitAndColorize(self, updateRealDist=True):
        # ADD NEW OBSTACLES
        for x,y in self.add_list:
            c = self.data[x][y]

            if c.queueing != QState.FW_QUEUED:
                if updateRealDist:
                    c.dist = 0
                c.sqdist = 0
                c.obstX = x
                c.obstY = y
                c.queueing = QState.FW_QUEUED
                c.voronoi = occupied
                self.q.push(0, (x,y))
        self.add_list = []
        
        # REMOVE OLD OBSTACLES
        for x,y in self.remove_list:
            c = self.data[x][y]

            if c.isOccupied(x,y):# obstacle was removed and reinserted
                continue
            self.q.push(0, (x,y))
            if updateRealDist:
                c.dist  = INFINITY
            c.sqdist = INT_MAX
            c.needsRaise = True                
                
        self.remove_list = []

    def marker_match_result(self, x, y):
        # implementation of connectivity patterns
        f = []

        #int nx, ny;
        #int dx, dy;

        i = 0
        count = 0
        v_count = 0
        v_count_four = 0
        
        #  int obstacleCount=0;
        for nx, ny in self.get_neighbors(x, y):
            nc = self.data[nx][ny]
            v = nc.voronoi
            b = v<=State.FREE and v!=State.PRUNE 
            #	if (v==occupied) obstacleCount++;
            f.append(b)
            if b:
                v_count+=1
                if nx==x or ny==y:
                    v_count_four += 1
                    count += 1
        
        if v_count<3 and v_count_four==1 and (f[1] or f[3] or f[4] or f[6]):
            #    assert(v_count<2);
            #    if (v_count>=2) printf("voro>2 %d %d\n", x, y);
            return MatchResult.KEEP

        # 4-connected
        if ((not f[0] and f[1] and f[3]) or (not f[2] and f[1] and f[4]) or (not f[5] and f[3] and f[6]) or (not f[7] and f[6] and f[4])):
            return MatchResult.KEEP
        if ((f[3] and f[4] and not f[1] and not f[6]) or (f[1] and f[6] and not f[3] and not f[4])):
            return MatchResult.KEEP

        # keep voro cells inside of blocks and retry later
        if voroCount>=5 and voroCountFour>=3 and data[x][y].voronoi!=State.RETRY:
            return MatchResult.RETRY

        return MatchResult.PRUNED

