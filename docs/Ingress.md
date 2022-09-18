# Ingress

Externall access to the cluster is handled using Nginx Ingress Controller.
The ingress controller is deployed in the `ingress-nginx` namespace.

All traffic goes through an AWS load balancer and the ingress does hostname based routing
to the relevant service.

TLS is handled using a wildcard certificate in AWS certificate manager with the domain
`*.dataforchange.org.il`. Ingress hostnames should define a CNAME record from the end
domain (e.g. `test.dataforchange.org.il`) to the load balancer hostname 
`k8s-main-ingress.dataforchange.org.il`.

## Exposing a non-http TCP Service

Use this method to expose a TCP service which is not HTTP, like a database:

1. Create a service of type `ClusterIP` for the service you want to expose.
2. Add a port mapping to the service in [/apps/ingress-nginx/controller-tcp-services-configmap.yaml](/apps/ingress-nginx/controller-tcp-services-configmap.yaml).
3. Add the port you added to the load balancer at [/apps/ingress-nginx/patch-controller-nlb-service.yaml](/apps/ingress-nginx/patch-controller-nlb-service.yaml).
4. Access the service at k8s-main-ingress.dataforchange.org.il:port
