.\aws cloudformation create-stack `
	--stack-name $($Args[0]) `
	--template-body file://$($Args[1]) `
	--parameters file://$($Args[2]) `
	--region=us-east-1
