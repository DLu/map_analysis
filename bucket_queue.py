MAXDIST = 1000
RESERVE = 64


class BucketQueue:
    """//! Priority queue for integer coordinates with squared distances as priority.
/** A priority queue that uses buckets to group elements with the same priority.
 *  The individual buckets are unsorted, which increases efficiency if these groups are large.
 *  The elements are assumed to be integer coordinates, and the priorities are assumed
 *  to be squared euclidean distances (integers).
 */"""
    square_indices = None
 
    def __init__(self):
        # make sure the index array is created
        if not BucketQueue.square_indices:
            BucketQueue.init_square_indices()
           
        self.nextBucket = 1E60
    
        # now create the buckets
        self.buckets = []
        for i in range(BucketQueue.numBuckets):
            self.buckets.append([])
        # reset element counter 
        self.count = 0
    
    def empty(self):
        return self.count == 0
    
    def push(self, priority, point):
        if priority >= len(BucketQueue.square_indices):
            print "error: priority %d is not a valid squared distance x*x+y*y, or x>MAXDIST or y>MAXDIST."% priority
            exit(-1)
            
        idx = BucketQueue.square_indices[priority]
        if idx<0:
            print "error: priority %d is not a valid squared distance x*x+y*y, or x>MAXDIST or y>MAXDIST."%priority
            exit(-1)

        self.buckets[idx].append(point)

        if (idx<self.nextBucket): 
            self.nextBucket = idx
        count+=1
    
    def pop(self):
        for i in range(self.nextBucket, len(self.buckets)):
            if len(self.buckets[i])!=0:
                break
        self.nextBucket = i
        self.count -= 1
        p = self.buckets[i].pop(0)
        return p

    @staticmethod
    def init_square_indices():
        a = [-1] * 2 * MAXDIST*MAXDIST+1
        count = 0
        for x in range(MAXDIST+1):
            for y in range(x+1):
                sqr = x*x + y*y
                a[sqr] = count
                count += 1
        BucketQueue.sqaure_indices = a
        BucketQueue.numBuckets = count
