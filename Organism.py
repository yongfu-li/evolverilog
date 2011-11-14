"""
    Class       : Computer Architecture, FALL 2011, Olin College
    Project     : 
    Author      : Shane Moon, Paul Booth
    Date        : 11/10/2011
    File Name   : OrganismManager.py
    Description :
"""

import random
import testOrgs

class Organism:
    def __init__(self, verilogFilePath, numInputs, numOutputs, 
        randomInit=False, nLayers=1, nGates=4, moduleName='organism'):
        
        self.verilogFilePath = verilogFilePath
        self.numInputs = numInputs
        self.numOutputs = numOutputs
        self.moduleName = moduleName
        self.fitness = None
        self.layers = [None]*nLayers
        self.nLayers=nLayers
        self.nGates=nGates
        if randomInit:
            self.randomInitialize(nLayers, nGates)

    def randomInitialize(self, nLayers, nGates):
        """
            Return Type: void
        """
        for layer in range(nLayers):
            self.layers[layer] = Layer(randomInit=True, nGates=nGates)

    def crossover(self, otherOrganism):
        """
            Return Type: <Organism>
            Crossovers self with another <Organism>, and returns a new
            <Organism>.
            Each layer of the resulting <Organism> is fully inherited from one parent.
        """
        
        # Needs to be implemented #
        
        randOrganism = BooleanLogicOrganism('TestCode/andTest.v',2,1,randomInit=True,moduleName='andTest')
        return randOrganism

    def mutate(self):
        """
            Return Type: <Organism>
        """
        return
        
    def compile(self, file, mainModule='andTest'):
        """
            Writes Organism to a verilog file.
        """
				#module ____;
				#    input _,_,_,_; (1 line)
				#    output _,_,_,_; (1 line)
				#    wire _,_,_,_; (layers-1 lines)
				#    and Name?
        
        
    def __str__(self):
        contents = '\n'.join(str(layer) for layer in self.layers)
        return 'Organism: {\n' + contents + '}'
    
    def fitnessFunction(self,inputs,actualOutputs,correctOutputs):
        raise NotImplementedError, 'Override this method in sub-classes.'
        
    def evaluate(self,correctResultMap):
        """
        Evaluates the fitness function of an organism if it has not
        already been evaluated.  The correctResultMap determines
        the correct mapping between inputs and outputs.
        
        Args:
            correctResultMap: testOrgs.SimulationMap
        
        Return type: <float> or <int> (number)
        """
        if self.fitness is None:
            #change the arguments on the line below or it will not compile
            simRes = testOrgs.testOrganism(
                self.verilogFilePath,
                'TestCode',
                self.numInputs,
                self.numOutputs,
                self.moduleName)
            
            inputs = []
            actualOutputs = []
            correctOutputs = []
            
            for trial in simRes.getTrials():
                currentInput = trial.getInputs()
                inputs.append(currentInput)
                actualOutputs.append(trial.getOutputs())
                correctOutputs.append(correctResultMap.getResult(currentInput))

            self.fitness = self.fitnessFunction(inputs,actualOutputs,correctOutputs)

        return self.fitness
            
    def getFitness(self):
        return self.fitness
        
    def __cmp__(self, other):
        return self.getFitness() - other.getFitness()
    
    def __hash__(self):
        return id(self)

class BooleanLogicOrganism(Organism):
    
    def fitnessFunction(self,inputs,actualOutputs,correctOutputs):
        
        score = 0.0
        for i, aOut, cOut in zip(inputs,actualOutputs,correctOutputs):
            if aOut == cOut:
                score += 1.0
        return score

class Layer:
    def __init__(self, randomInit=False, nGates=4):
        self.gates = [None]*nGates
        if randomInit:
            self.randomInitialize(nGates)

    def randomInitialize(self, nGates):
        for gate in range(nGates):
            self.gates[gate] = Gate(randomInit=True, nInputs=nGates)  #In this case, we assume nGates maps to nInputs
            
    def addGate(self, gate):
        self.gates.append(gate)
        
    def retGate(self, num):
        return self.gates[num]

    def crossover(self, otherLayer):
        """
            Return Type: <Layer>
            Crossovers self with another <Layer>, and returns a new <Layer>
        """
        offspring = Layer(nGates=0)
        for gate in range(len(self.gates)):
            offspring.addGate(random.choice([self.retGate(gate), otherLayer.retGate(gate)]))
        return offspring
        
    def __str__(self):
        contents = ' '.join(str(gate) for gate in self.gates)
        return 'Layer:[ ' + contents + ']'


class Gate:
    
    # type followed by number of inputs
    gateChoices = [
        ('and',2),
        ('or',2),
        ('not',1),
        ('buf',1)
        ]
    
    def __init__(self, randomInit=False, nInputs=4):
        self.inputConnections = []
        self.gateType = ''
        if randomInit:
            self.randomInitialize(nInputs)
            

    def randomInitialize(self, nInputs):
        """
            Return Type: void
            Randomly initializes its instruction and connection
            Assumes there are no prior connections
        """
        choice = random.choice(self.gateChoices)
        self.gateType = choice[0]
        for connection in range(choice[1]):
            self.inputConnections.append(random.randint(1,nInputs))
            
    def __str__(self):
        return self.gateType+str(self.inputConnections)
        
if __name__ == '__main__':
    testOrganism = BooleanLogicOrganism('TestCode/andTest.v',2,1,randomInit=True,moduleName='andTest')
    print testOrganism
    
    defaultResult = testOrgs.testOrganism('TestCode/andTest.v', '.', 2, 1, 'andTest',clearFiles=True)
    simMap = testOrgs.SimulationMap(defaultResult)
    
    print testOrganism.evaluate(simMap)
