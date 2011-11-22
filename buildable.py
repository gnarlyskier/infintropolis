import copy

import inf


class Buildable:
    """Represents an buildable game object.

    Edge
    d = {t, c, b}
     t  /\ 
    c  |  |
     b  \/

    Vertex
    d = {t, b}
     t ./\ 
       |  |
     b '\/
    """
    pos = None
    level = None
    block = None
    nationName = None
    capitolNum = None
    validate = False

    def __init__(self, blockPos, pos, level, nationName=None, capitolNum=None,
                 validate=True):
        self.pos = pos.copy()
        self.block = blockPos.copy()
        self.level = int(level)
        self.nationName = nationName
        self.capitolNum = capitolNum
        self.validate = validate

    def build(self, worldshard, nation, capitol):
        """Adds this buildable in all necessary database models."""
        self.nationName = nation.getName()
        self.capitolNum = capitol.getNumber()
        block = worldshard.getBlock(self.block)
        if not block.worldshard:
            print "\nReally no worldshard"
        if block and self.checkBuild(worldshard):
            block.atomicBuildCost(self, nation.getColors(), capitol)

    def gather(self, worldshard, roll, resources):
        """Add resources gathered for this roll to the resource list."""
        if not self.isGatherer():
            return
        for v in self.pos.getSurroundingTiles():
            t = worldshard.getTile(self.block, v)
            if t and t.roll == roll:
                i = inf.TileType.typeToResource[t.tiletype]
                if i is not None:
                    resources[i] += BuildType.gatherMult[self.level]

    def isUpgrade(self):
        """Returns True if this buildable type is an upgrade."""
        return not self.isShip() and BuildType.isUpgrade[self.level]

    def isGatherer(self):
        """Returns true if this buildable can gather resources."""
        return not self.isShip() and BuildType.gatherMult[self.level]
               
    def getCost(self):
        """Returns the cost of this buildable as a list."""
        if not self.validate:
            return [0, 0, 0, 0, 0, 0]
        else:
            return BuildType.costList[self.level]

    def checkBuild(self, worldshard):
        """Checks if this buildable can be built."""
        if not self.validate:
            return True
        # Perform type-specific validation.
        if self.level == BuildType.settlement:
            return self._checkBuildVertex(worldshard)
        elif self.level == BuildType.road:
            return self._checkBuildEdge(worldshard, BuildType.road)
        elif self.level == BuildType.port:
            return self._checkBuildVertex(worldshard, requireWater=True)
        elif self.isShip():
            return self._checkBuildShip(worldshard)
        elif self.isUpgrade():
            return self._checkUpgradeCity(worldshard)
        else:
            return False

    def _checkBuildShip(self, worldshard):
        """Check if this buildable can be built as a ship."""
        wtile = worldshard.getTile(self.block, self.pos)
        return wtile and wtile.isWater() and\
               worldshard.checkBuildableRequirements(self.block, self.pos,
                ((-1, BuildType.topVertex, self.nationName, self.capitolNum),
                 (-1, BuildType.bottomVertex, self.nationName, self.capitolNum),
                 (0, BuildType.topVertex, self.nationName, self.capitolNum),
                 (0, BuildType.bottomVertex, self.nationName, self.capitolNum),
                 (1, BuildType.bottomVertex, self.nationName, self.capitolNum),
                 (5, BuildType.topVertex, self.nationName, self.capitolNum)),
                ((-1, BuildType.middle),))

    def _checkBuildVertex(self, worldshard, requireWater=False):
        """Check if this buildable can be built at a vertex."""
        if self.pos.d == BuildType.topVertex:
            return worldshard.checkBuildableRequirements(self.block, self.pos,
                ((-1, BuildType.centerEdge, self.nationName, self.capitolNum),
                 (-1, BuildType.topEdge, self.nationName, self.capitolNum),
                 (2, BuildType.bottomEdge, self.nationName, self.capitolNum)),
                ((-1, BuildType.topVertex),
                 (-1, BuildType.bottomVertex),
                 (1, BuildType.bottomVertex),
                 (2, BuildType.bottomVertex)),
                 requireLand=True, requireWater=requireWater)
        elif self.pos.d == BuildType.bottomVertex:
            return worldshard.checkBuildableRequirements(self.block, self.pos,
                ((-1, BuildType.centerEdge, self.nationName, self.capitolNum),
                 (-1, BuildType.bottomEdge, self.nationName, self.capitolNum),
                 (4, BuildType.topEdge, self.nationName, self.capitolNum)),
                ((-1, BuildType.topVertex),
                 (-1, BuildType.bottomVertex),
                 (4, BuildType.topVertex),
                 (5, BuildType.topVertex)),
                 requireLand=True, requireWater=requireWater)
        else:
            return False

    def _checkBuildEdge(self, worldshard, level):
        """Check if this buildable can be built at an edge."""
        # Determine land/water requirements.
        rland = False
        rwater = False
        if level == BuildType.road:
            rland = True
        # Perform verification.
        if self.pos.d == BuildType.topEdge:
            return worldshard.checkBuildableRequirements(self.block, self.pos,
                ((-1, BuildType.topVertex, self.nationName, self.capitolNum),
                 (1, BuildType.bottomVertex, self.nationName, self.capitolNum),
                 (-1, BuildType.centerEdge, self.nationName, self.capitolNum,
                  level),
                 (2, BuildType.bottomEdge, self.nationName, self.capitolNum,
                  level),
                 (1, BuildType.centerEdge, self.nationName, self.capitolNum,
                  level),
                 (1, BuildType.bottomEdge, self.nationName, self.capitolNum,
                  level)),
                ((-1, BuildType.topEdge),),
                requireLand=rland, requireWater=rwater)
        elif self.pos.d == BuildType.centerEdge:
            return worldshard.checkBuildableRequirements(self.block, self.pos,
                ((-1, BuildType.topVertex, self.nationName, self.capitolNum),
                 (-1, BuildType.bottomVertex, self.nationName, self.capitolNum),
                 (-1, BuildType.topEdge, self.nationName, self.capitolNum,
                  level),
                 (-1, BuildType.bottomEdge, self.nationName, self.capitolNum,
                  level),
                 (2, BuildType.bottomEdge, self.nationName, self.capitolNum,
                  level),
                 (4, BuildType.topEdge, self.nationName, self.capitolNum,
                  level)),
                ((-1, BuildType.centerEdge),),
                requireLand=rland, requireWater=rwater)
        elif self.pos.d == BuildType.bottomEdge:
            return worldshard.checkBuildableRequirements(self.block, self.pos,
                ((-1, BuildType.bottomVertex, self.nationName, self.capitolNum),
                 (5, BuildType.topVertex, self.nationName, self.capitolNum),
                 (-1, BuildType.centerEdge, self.nationName, self.capitolNum,
                  level),
                 (4, BuildType.topEdge, self.nationName, self.capitolNum,
                  level),
                 (5, BuildType.centerEdge, self.nationName, self.capitolNum,
                  level),
                 (5, BuildType.topEdge, self.nationName, self.capitolNum,
                  level)),
                ((-1, BuildType.bottomEdge),),
                requireLand=rland, requireWater=rwater)
        else:
            return False
            
    def _checkUpgradeCity(self, worldshard):
        """Check if this buildable can upgrade the current location."""
        return worldshard.checkBuildableRequirements(self.block, self.pos,
            ((-1, self.pos.d, self.nationName, self.capitolNum,
              BuildType.settlement),),
            ())

    def copy(self):
        return copy.copy(self)

    def getList(self):
        """Returns the pos and level as a list."""
        l = self.pos.getList()
        l.append(self.level)
        return l

    def isInCapitol(self, nation, capitolNumber):
        """Returns True if this buildable is in the given nation's capitol."""
        return nation == self.nationName and capitolNumber == self.capitolNum

    def isShip(self):
        """Is this buildable a ship."""
        return self.pos.d == BuildType.middle


class BuildType:
    """Enum for buildable types."""
    topEdge, centerEdge, bottomEdge, topVertex, bottomVertex, middle = range(6)
    dToJSON = ['t', 'c', 'b', 't', 'b', 'm']
    JSONtod = ['t', 'c', 'b', 'tv', 'bv', 'm']

    empty = -1
    settlement, city, road, port,\
    sloop = range(5)
    tToJSON = ['s', 'c', 'r', 'p',
               'f']
    LOSVision = [15, 18, 8, 15,
                  4]
    gatherMult = [1, 2, 0, 0]
    isUpgrade = [False, True, False, False]
    stationarySet = frozenset(['s', 'c', 'r', 'p'])
    vertexSet = frozenset(['s', 'c', 'p'])

    costList = [ [-1, -1, -1, -1,  0,  0],
                 [ 0,  0,  0, -2, -3,  0],
                 [-1,  0, -1,  0,  0,  0],
                 [-1, -1,  0,  0, -2,  0],
                 
                 [ 1,  1,  0,  0,  0,  0] ]


def JSONtod(jsont, jsond):
    """Get the correct d value from a json d value."""
    v = jsond
    if jsont in BuildType.vertexSet:
        v += 'v'
    return BuildType.JSONtod.index(v)
