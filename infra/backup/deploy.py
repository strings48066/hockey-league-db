import boto3

def deploy_cloudformation_stack(stack_name, template_file):
    try:
        # Read the CloudFormation template from the file
        with open(template_file, 'r') as file:
            template_body = file.read()

        client = boto3.client('cloudformation')

        # Deploy the CloudFormation stack
        response = client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_NAMED_IAM'],
        )

        # Wait until the stack is created
        waiter = client.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack_name)

        print(f"Stack {stack_name} has been created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    stack_name = 'hockey-db-storage'
    template_file = 's3.yml'

    deploy_cloudformation_stack(stack_name, template_file)