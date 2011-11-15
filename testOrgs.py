import sys, os, subprocess, glob

simulationTemplate="""// auto-generated by evolverilog
`include "%s" // include the module to call

module organismSimulator;

    reg %s; // number of Inputs Args
    wire %s; // number of Outputs Args
    
    parameter settleDelay = 10000;
    
    %s uut (%s,%s); // module to call, number of Output, Input Args
    
    integer i;
    
    initial
    begin
        $display (%s); // io structure
        // should run number of inputs ^ 2 times
        for (i = 0; i < %d; i = i + 1) begin
            {%s} = i; // number of Input Args
            #settleDelay
            $display ("%s",%s,%s); // total args, outputs, inputs 
        end
    end
    
endmodule"""

def writeSimulation(verilogTestOutputFile,organismModuleFile,
    numInputs,numOutputs,organismModuleName=None):
    
    if organismModuleName is None:
        organismModuleName = organismModuleFile.split('.')[0]
    
    totalArgs = numInputs+numOutputs
    inputs = ','.join('Input%d'%i for i in xrange(numInputs))
    outputs = ','.join('Output%d'%i for i in xrange(numOutputs))
    display = ','.join('%d' for i in xrange(totalArgs))
    ioStructure = '"'+','.join('out' if i < numOutputs else 'in' for i in xrange(totalArgs) )+'"'
    
    templateArgs = (organismModuleFile,inputs,outputs,organismModuleName,
        outputs,inputs,ioStructure,numInputs**2,inputs,display,outputs,
        inputs)
    
    simulationCode = simulationTemplate%templateArgs
    
    f = open(verilogTestOutputFile,'w')
    f.write(simulationCode)
    f.close()

def getSimulationResultFromFile(filepath):
    
    fin = open(filepath,'r')
    txt = fin.read()
    fin.close()
    
    return getSimulationResultFromText(txt)

def getSimulationResultFromText(txt):
    
    lines = txt.split('\n')
    
    # reads first line (contains formatting information)
    ioStructure = lines[0].split(',')
    numberOfInputs = ioStructure.count("in")
    numberOfOutputs = ioStructure.count("out")
    
    s = SimulationResult(numberOfInputs,numberOfOutputs)
    
    # will go through lines 1:END (Note: last element is EOF)
    for line in lines[1:-1]:
        simResults = line.strip(' ').split(',') # csv format
        s.addTrial(
            SimulationTrial(
                tuple(int(a) for a in simResults[0:numberOfOutputs]),
                tuple(int(b) for b in simResults[numberOfOutputs:])
            )
        )
        
    return s

class SimulationMap:
    
    def __init__(self,simulationResult):
        
        self._map = dict( 
            ( tuple( t.getInputs() ),tuple( t.getOutputs() ) ) 
            for t in simulationResult.getTrials()
            )
            
    def getResult(self,inputTuple):
        return self._map[tuple(inputTuple)]
    
    def __str__(self):
        return str(self._map)

class SimulationResult:
    
    def __init__(self,numInputs,numOutputs):
        
        self._trials = []
        self._numberOfInputs = 0
        self._numberOfOutputs = 0
    
    def addTrial(self,simTrial):
        self._trials.append(simTrial)
        
    def getTrials(self):
        return self._trials
        
    def __str__(self):
        return '\n'.join(["Trial %d: %s"%(i,str(trial)) for i,trial in enumerate(self.getTrials())])

class SimulationTrial:
    
    def __init__(self,outputs,inputs):
        
        self._inputs = inputs
        self._outputs = outputs
        
    def getInputs(self):
        return self._inputs
        
    def getOutputs(self):
        return self._outputs
        
    def __str__(self):
        return "Inputs: %s. Outputs: %s"%(str(self.getInputs()),str(self.getOutputs()))

def testOrganism(filepath, subdir, numInputs, numOutputs, 
    organismModuleName, clearFiles=True, testFileName = 'organismTest'):

    # write the verilog test file
    writeSimulation(
        os.path.join(subdir,'%s.v'%testFileName),
        filepath,
        numInputs,
        numOutputs,
        organismModuleName
        )
    
    # print 'Testing organism: %s'%filepath

    # compile the test file
    subprocess.call([
        'iverilog', '-o', 
        os.path.join(subdir,'%s.o'%testFileName),
        os.path.join(subdir,'%s.v'%testFileName)]
        )
    # get the test file results
    process = subprocess.Popen([
        'vvp',
        os.path.join(subdir,'%s.o'%testFileName)],
        stdout=subprocess.PIPE
        )
    # pull output from pipe
    output = process.communicate() #(stdout, stderr)
    
    # convert into a SimulationResult from pipe output
    simResult = getSimulationResultFromText('\n'.join(output[0].split('\r\n')))
    # print simResult
    
    if clearFiles:
        os.remove(os.path.join(subdir,'%s.o'%testFileName))
        os.remove(os.path.join(subdir,'%s.v'%testFileName))
    
    return simResult

def testOrganisms(subdir,numInputs,numOutputs,organismModuleName,
    testFileName = 'organismTest'):
	"""
	Run the evolverilog test suite in a subdirectory.
	"""
	
	allResults = {}

    # for all files with a verilog extension, test the organism
	for file in glob.glob(os.path.join(subdir, '*.v')):
		allResults[file] = testOrganism(file,subdir,numInputs,
            numOutputs,organismModuleName)
	# print allResults.keys()
	
	os.remove(os.path.join(subdir,'%s.o'%testFileName))
	os.remove(os.path.join(subdir,'%s.v'%testFileName))

if __name__ == "__main__":
	testOrganisms(sys.argv[1],2,1,'andTest')
