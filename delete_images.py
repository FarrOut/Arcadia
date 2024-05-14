import boto3

# Create an EC2 Image Builder client
image_builder = boto3.client('imagebuilder')
ec2 = boto3.client('ec2')

# Get a list of all the images
response = image_builder.list_images()
images = response['imageVersionList']

image_name_pattern = 'rising-storm-2-vietnam-dedicated-server'

print(images)

# Delete each image
for image in images:
    image_arn = image['arn']
    try:
        if image_name_pattern in image_arn:     
            try:
                # Deregister AMI
                deregister_response = ec2.deregister_image(ImageId=image_arn)
            except Exception as e:
                print(f"Error deregistering image : {e}")           
                raise e     

            # Delete the image
            response = image_builder.delete_image(imageBuildVersionArn=image_arn)                   
            print(f"Deleted image: {image_arn}")
    except Exception as e:
        print(f"Error deleting image {image_arn}: {e}")
