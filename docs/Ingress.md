# Ingress

Externall access to the cluster is handled using Nginx Ingress Controller.
The ingress controller is deployed in the `ingress-nginx` namespace.

All traffic goes through an AWS load balancer and the ingress does hostname based routing
to the relevant service.

TLS is handled using a wildcard certificate in AWS certificate manager with the domain
`*.dataforchange.org.il`. Ingress hostnames should define a CNAME record from the end
domain (e.g. `test.dataforchange.org.il`) to the load balancer hostname 
`k8s-main-ingress.dataforchange.org.il`.
