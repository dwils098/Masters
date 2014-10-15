Google App Engine:
	Client Capabilities:
		- Google Web Toolkit:
			Development toolkit for building and optimizing complex
			browser-based applications.
		- Google Gadgets:
			Dynamic web content that can be embedded on a webpage.
			
	Cloud Computing Services:
		- Google App Engine (GAE):
			-> Python & Django
			-> Dynamic and Scalable Runtime
			
	Support Service:
		- GAE Datastore:
			Schema-less object datastore, with scalable storage, a rich modelling API
			and an SQL-Like query language.
		- GData:
			Deprecated custom Data handling API (very REST-like).	
		- Google Accounts.
		- Social Graph API.
		- Others:
			-> MEMCACHE: short-term storage, stores data in a server's memory allowing
			for faster access compare to the datastore. (Non-Persistent)
			-> Scheduled Tasks and Task Queues.
			-> BLOBSTORE: (Binary Large Object) for video and big files (up to 2Gb).
			
	
	NOTES:
		Runtime Environment:
		GAE runtime environment presents itself as the place where the actual application is executed. The application is only invoked once an HTTP request is processed to the GAE via a web browser or some other interface, meaning that the application is not constantly running if no invocation or processing has been done. In case of such HTTP request, the request handler forwards the request and the GAE selects one out of many possible Google servers where the application is then instantly deployed and executed for a certain amount of time. 
		
		

Amazon Beanstalk:
	Cloud Computing Services:
		- Elastic Compute Cloud (EC2)
			-> OnDemand Instances
			-> Machine Images.
	Support Services:
		- Simple Storage Service (S3) (simple web-services interface for storage)
		- SimpleDB (non-relational data store)
		- CloudFront (content delivery webService)
		- SimpleQueue Service (SQS) (message queuing service)
		