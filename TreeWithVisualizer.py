"""
    Class       : Computer Architecture, FALL 2011, Olin College
    Project     : EvolVerilog
    Author      : Paul Booth, Shane Moon
    Date        : 11/17/11
    File Name   : Tree.py
    Description : It's a tree to be evolved!

    
"""
import random
from copy import deepcopy
import ete2a1 as ete2

class Tree:
    def __init__(self, numOrganismInputs, maxDepth, inputProbability):
        self.root = Node(None, numOrganismInputs, 0, maxDepth, inputProbability)

    def __str__(self):
        raw = self.root.__str__()
        t = ete2.Tree("(" + raw + ")out;", format=1)
        return "Raw string (read from the end):\n%s \n\nVisualization:\n %s" \
                %(raw, t.get_ascii(show_internal=True))

    def count(self):
        return self.root.count()

    def crossover(self, other):
        """
            Return Type: <Tree>
        """
        child = deepcopy(self)
        nodeList = child.toList()
        otherNodeList = other.toList()
        childNode = random.choice(nodeList)
        otherNode = deepcopy(random.choice(otherNodeList))
        #print "child node index: " + str(childNodeIndex)
        #print "other node index: " + str(otherNodeIndex)
        #childNode = random.choice(nodeList)
        #otherNode = deepcopy(random.choice(otherNodeList))
        # we need a deepcopy because we don't want to alter original Tree
        childNode.replaceSelf(otherNode)
        return child

    def mutate(self):
        """
            Return Type: void
            Selects one of the <Node>s in a <Tree>, and replaces it with
            a new random <Node>.
        """
        nodeList = self.toList()
        mutantNodeIndex = random.randint(0,len(nodeList)-1)
        mutantNode = nodeList[mutantNodeIndex]

        # Create a new random <Node>.
        #if (mutantNode.depth == mutantNode.maxDepth):
        #    newNode = InputNode(mutantNode.parent, mutantNode.numOrganismInputs,
        #                        mutantNode.depth,  mutantNode.maxDepth,
        #                        mutantNode.inputProbability)
        #else:
        if (random.random() > mutantNode.inputProbability):
            newNode = Node(mutantNode.parent, mutantNode.numOrganismInputs,
                           mutantNode.depth,  mutantNode.maxDepth,
                           mutantNode.inputProbability)
        else:
            newNode = InputNode(mutantNode.parent, mutantNode.numOrganismInputs,
                                mutantNode.depth,  mutantNode.maxDepth,
                                mutantNode.inputProbability)

        # Replace the chosen <Node> with the new <Node>
        mutantNode.replaceSelf(newNode)
    
    def toList(self):
        """
            Return Type: <List> of <Node>s (of the self <Tree>)
        """
        return self.root.toList()
    
    def toVerilog(self,treeNum):
        return self.root.toVerilog(treeNum,'0')[0]

    def visualize(self, filename):
        """
            Return Type: void
            Visualize a tree and save it as a .png file
        """
        raw = self.root.__str__()
        tree = ete2.Tree("(" + raw + ")out;", format=1)
        nodes = tree.get_descendants()
        nodes.append(tree)
        
        ts = ete2.TreeStyle()
        ts.show_leaf_name = False
        
        for c in nodes:
            tf = ete2.TextFace(c.name)
            tf.margin_left = 15
            c.add_face(tf, column=0, position="branch-top")
        
        tree.show(tree_style=ts)
        tree.render(filename, tree_style=ts)

        
class Node:
    # Could include gate probabilities or weights so that buf is less likely
    # than and or xor
    gateChoices = [
            ('and',(2,2)),
            ('or',(2,2)),
            ('not',(1,1)),
            ('nand',(2,2)),
            ('xor',(2,2)),
            ('buf', (1,1))
            ]

    def __init__(self, parent, numOrganismInputs, depth, maxDepth, inputProbability):
        self.parent = parent
        self.children = []
        self.numOrganismInputs = numOrganismInputs
        self.depth = depth
        self.randomizeGate()
        self.inputProbability = inputProbability
        self.maxDepth = maxDepth
        self.isInputNode = False
        self.makeChildren(maxDepth)

    def __str__(self):
        s = ""
        if (not self.isInputNode):
            s += "("
            for child in self.children:
                s +=  child.__str__() + ","

            if (len(self.children) > 0):
                s = s[0:-1] + ")"
            else:
                s += ")"
        return s + self.gate

    def count(self):
        count = 1
        for child in self.children:
            count += child.count()
        return count

    def toList(self):
        lst = [self]
        for child in self.children:
            lst.extend(child.toList())
        return lst

    def replaceChild(self, oldNode, newNode):
        found = False
        for i in range(len(self.children)):
            child = self.children[i]
            if (child == oldNode):
                newNode.parent = self
                self.children[i] = newNode
                found = True
        if (not found):
            raise "hell. The replaceChild is broken and couldn't find" \
                  " the old node."

    def replaceSelf(self, newNode):
        if (self.parent):
            self.parent.replaceChild(self, newNode)
        else:
            self = newNode
            self.parent = None

    def randomizeGate(self):
        self.gate, inputRange = random.choice(self.gateChoices)
        self.numberOfInputs = random.randint(inputRange[0], inputRange[1])

    def makeChildren(self, maxDepth):
        # Could change the inputProbability passed to children to approach 1
        # more depth , means more likely to terminate the tree
        for i in range(self.numberOfInputs):
            if (self.depth < maxDepth and random.random() > self.inputProbability):
                self.children.append(
                    Node(self, self.numOrganismInputs,
                        self.depth + 1, maxDepth, self.inputProbability)
                    )
            else:
                self.children.append(
                    InputNode(self, self.numOrganismInputs,
                        self.depth + 1, maxDepth, self.inputProbability)
                    )
    
    def toVerilog(self,treeNum,branchStr):
        """
        Each node needs to know the branch number of its children's
        outputs and the tree number (or id).
        
        Each node needs to know its branch number in the tree and
        the tree number (or id).
        
        Outputs: verilog,outputStr
        """
        
        verilogRes = []
        inputs = []
        for childNum, child in enumerate(self.children):
            v,output = child.toVerilog(treeNum,'%s%d'%(branchStr,childNum))
            if v != '':
                verilogRes.append(v)
            inputs.append(output)
        
        inputStr = ','.join(inputs)
        
        if len(branchStr) > 1:
            outputStr = 'output%d_branch%s'%(treeNum,branchStr)
        else:
            outputStr = 'output%d'%treeNum
            
        verilogRes.append('\t%s #50 (%s,%s);'%(self.gate,outputStr,inputStr))
        return ('\n'.join(verilogRes),outputStr)

class InputNode(Node):
    def __init__(self, parent, numOrganismInputs, depth, maxDepth, inputProbability):
        Node.__init__(self, parent, numOrganismInputs, depth, maxDepth, inputProbability)
        self.isInputNode = True
        
    def randomizeGate(self):
        self.inputIndex = random.randint(0, self.numOrganismInputs - 1)
        self.numberOfInputs = 0
        self.gate = "input" + str(self.inputIndex)
        
    def toVerilog(self,treeNum,branchStr):
        """
        Each node needs to know the branch number of its children's
        outputs and the tree number (or id).
        
        Each node needs to know its branch number in the tree and
        the tree number (or id).
        
        Outputs: verilog,outputStr
        """
        
        return ('','input%d'%self.inputIndex)

if __name__ == '__main__':
    tree = Tree(4, 3, 0.1)
    print "tree1"
    print tree
    tree.visualize('test.png')
