module test(output0,output1,output2,output3,input0,input1,input2,input3);

	output output0,output1,output2,output3;
	input input0,input1,input2,input3;

	wire output0,output1,output2,output3;

	not #50 (output0,input2);
	not #50 (output1,input1);
	and #50 (output2,input3,input1);
	not #50 (output3,input2);

endmodule