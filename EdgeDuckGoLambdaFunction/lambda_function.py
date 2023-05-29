import boto3
import re
from io import BytesIO
#from lxml import etree
from zipfile import ZipFile
#from docx import Document

def lambda_handler(event, context):
    # Get the uploaded file details
    s3 = boto3.client('s3')
    
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Read the file from S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    file_data = response['Body'].read()
    
    # Determine the file extension and handle different naming styles
    file_extension = re.search(r'\.(\w+)$', object_key.lower()).group(1)
    
    if file_extension == 'txt':
        word_count = count_words_text(file_data)
    elif file_extension == 'docx':
        word_count = count_words_docx(file_data)
    elif file_extension == 'zip':
        word_count = count_words_zip(file_data)
    else:
        word_count = 0
        
    
    # Send notification using Amazon SNS
    sns = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-west-2:020407725987:topic-duckedge'  # Replace with your SNS topic ARN
    message = 'New file uploaded: {}\nWord count: {}'.format(object_key, word_count)
    
    sns.publish(TopicArn=topic_arn, Message=message)
    print("Notification sent successfully.")

def count_words_text(file_data):
    text = file_data.decode('utf-8')
    words = text.split()
    return len(words)

def count_words_docx(file_data):
    document = Document(BytesIO(file_data))
    words = [p.text for p in document.paragraphs]
    words = [word for word in words if word.strip()]
    return len(words)

def count_words_zip(file_data):
    zip_file = ZipFile(BytesIO(file_data))
    word_count = 0

    for file in zip_file.namelist():
        if file.endswith('.txt'):
            text_data = zip_file.read(file)
            word_count += count_words_text(text_data)

    return word_count

