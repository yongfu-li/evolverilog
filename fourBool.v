module fourBool(output0,output1,output2,output3,input0,input1,input2,input3);

	output output0,output1,output2,output3;
	input input0,input1,input2,input3;

	wire output0,output1,output2,output3;

<<<<<<< HEAD
	buf #50 (output0,input1);
	or #50 (output1,input0,input3);
	nand #50 (output2,input1,input2);
	not #50 (output3,input1);
=======
	or #50 (output0,input0,input1);
	and #50 (output1,input1,input1);
	nand #50 (output2,input2,input1);
	xor #50 (output3,input0,input3);
>>>>>>> 60319a1ec2c528f44c982ed6ee73aafdcec556e4

endmodule