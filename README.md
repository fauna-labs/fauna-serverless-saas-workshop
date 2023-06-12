# AWS Serverless SaaS Architecture Workshop

In this workshop you will be building a multi-tenant Software-as-a-Service (SaaS) solution using Fauna and AWS Serverless Services, specifically Amazon API Gateway, Amazon Cognito, AWS Lambda, AWS CodePipeline, and Amazon CloudWatch. The diagram below describes at a high-level, the reference architecture; And we walk you through the entire solution. The goal is to provide an understanding of serverless architecture as it apples to multi-tenancy, and introduce Fauna features/functionality that make them seamless to implement.

![Architecture Diagram](/images/ServerlessSaas-Final.png)

## Navigating the workshop

Navigate into each Lab's folder and follow along the instructions. 

The workshop's infrastructure and underlying sample apps buildout sequentially, i.e. we start with a basic full-stack app in Lab 1, and continue to add more capabilities in subsequent labs. As such, it is best to work through the Labs sequentially. However, each Lab comes with self-contained CloudFormation files and deployment scripts such that you can deploy any lab without any dependency on deploying a prior one.

---

> This workshop is a fork of the [SaaS Factory Serverless SaaS reference solution](https://github.com/aws-samples/aws-saas-factory-ref-solution-serverless-saas), combined with Fauna concepts. The combination produces an architecture that’s both scalable yet highly flexible (at the database layer), allowing requirements to effortlessly change over time, while providing the best developer experience.
