**Note:** For the screenshots, you can store all of your answer images in the `answer-img` directory.

Firstly, set up Vagrant on your machine. 
Use `vagrant ssh` to ssh on vagrant machine.

## Set up a kube-context on your machine

Use `cat etc/rancher/k3s/k3s.yaml` to get the content of the file on vagrant machine and get a copy and create or replace `~/.kube/config` on your host machine.
Use `kubectl describe services` to test the k3s cluster is working properly.

```
PS D:\udacity\metric_dashboard> kubectl describe services
Name:              kubernetes
Namespace:         default
Labels:            component=apiserver
                   provider=kubernetes
Annotations:       <none>
Selector:          <none>
Type:              ClusterIP
IP Family Policy:  SingleStack
IP Families:       IPv4
IP:                10.43.0.1
IPs:               10.43.0.1
Port:              https  443/TCP
TargetPort:        6443/TCP
Endpoints:         10.0.2.15:6443
Session Affinity:  None
Events:            <none>
```
## Install Helm

```
vagrant@master:~> curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
vagrant@master:~> ls
bin  get_helm.sh
vagrant@master:~> chmod 700 get_helm.sh
vagrant@master:~> ./get_helm.sh
Downloading https://get.helm.sh/helm-v3.7.2-linux-amd64.tar.gz
Verifying checksum... Done.
Preparing to install helm into /usr/local/bin
helm installed into /usr/local/bin/helm
vagrant@master:~>  helm version
version.BuildInfo{Version:"v3.7.2", GitCommit:"663a896f4a815053445eec4153677ddc24a0a361", GitTreeState:"clean", GoVersion:"go1.16.10"}
```
## Installing Grafana and Prometheus

```
vagrant@master:~> kubectl create namespace monitoring
namespace/monitoring created
vagrant@master:~> helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
"prometheus-community" has been added to your repositories
vagrant@master:~> helm repo add stable https://charts.helm.sh/stable
"stable" has been added to your repositories
vagrant@master:~> helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "stable" chart repository
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈Happy Helming!⎈
vagrant@master:~> helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --kubeconfig /etc/rancher/k3s/k3s.yaml
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /etc/rancher/k3s/k3s.yaml
WARNING: Kubernetes configuration file is world-readable. This is insecure. Location: /etc/rancher/k3s/k3s.yaml
W1212 09:01:34.258061   20270 warnings.go:70] policy/v1beta1 PodSecurityPolicy is deprecated in v1.21+, unavailable in v1.25+
NAME: prometheus
LAST DEPLOYED: Sun Dec 12 09:00:32 2021
NAMESPACE: monitoring
STATUS: deployed
REVISION: 1
NOTES:
kube-prometheus-stack has been installed. Check its status by running:
  kubectl --namespace monitoring get pods -l "release=prometheus"

Visit https://github.com/prometheus-operator/kube-prometheus for instructions on how to create & configure Alertmanager and Prometheus instances using the Operator.
vagrant@master:~>   kubectl --namespace monitoring get pods -l "release=prometheus"
NAME                                                   READY   STATUS    RESTARTS   AGE
prometheus-prometheus-node-exporter-l4lss              1/1     Running   0          41s
prometheus-kube-prometheus-operator-85757cb64f-w2ztv   1/1     Running   0          40s
```
Run `kubectl --namespace monitoring port-forward service/prometheus-grafana --address 0.0.0.0 30000:80` to access the grafana. You can access Grafana in host machine using this `localhost:30000` url.

## Install Jaeger

```vagrant@master:~> kubectl create namespace observability
namespace/observability created
vagrant@master:~> kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/crds/jaegertracing.io_jaegers_crd.yaml
customresourcedefinition.apiextensions.k8s.io/jaegers.jaegertracing.io created
vagrant@master:~> kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/service_account.yaml
serviceaccount/jaeger-operator created
vagrant@master:~> kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/role.yaml
role.rbac.authorization.k8s.io/jaeger-operator created
vagrant@master:~> kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/role_binding.yaml
rolebinding.rbac.authorization.k8s.io/jaeger-operator created
vagrant@master:~> kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy//operator.yaml
deployment.apps/jaeger-operator created
vagrant@master:~> kubectl get all -n observability
NAME                                   READY   STATUS    RESTARTS   AGE
pod/jaeger-operator-694cbbb886-hcf9r   1/1     Running   0          3m21s

NAME                              TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)             AGE
service/jaeger-operator-metrics   ClusterIP   10.43.69.23   <none>        8383/TCP,8686/TCP   109s

NAME                              READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/jaeger-operator   1/1     1            1           3m21s

NAME                                         DESIRED   CURRENT   READY   AGE
replicaset.apps/jaeger-operator-694cbbb886   1         1         1       3m21s

```
## Cluster wide Jaeger

```
vagrant@master:~> kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/cluster_role.yaml
clusterrole.rbac.authorization.k8s.io/jaeger-operator created
vagrant@master:~> kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/cluster_role_binding.yaml
clusterrolebinding.rbac.authorization.k8s.io/jaeger-operator created
```
## Deploying the Application

```
master:/vagrant/manifests # kubectl apply -f app/
deployment.apps/backend-app created
service/backend-service created
deployment.apps/frontend-app created
service/frontend-service created
deployment.apps/trial-app created
service/trial-service created
```

## Exposing Grafana

```
master:/vagrant/manifests # kubectl get pod -n monitoring | grep grafana
prometheus-grafana-65d9fdd465-z6qdz
master:/vagrant/manifests # kubectl port-forward -n monitoring service/prometheus-grafana --address 0.0.0.0 30000:80
```

## Creating the Jaeger Instance

```
kubectl apply -n observability -f - <<EOF
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: simplest
EOF
```
You can access Jaeger in browser of host machine using `kubectl port-forward -n observability $(kubectl get pods -n observability -l=app="jaeger" -o name) --address 0.0.0.0 16686` command.

## Exposing the application

```
kubectl apply -f app/
kubectl port-forward service/frontend-service --address 0.0.0.0 30001:8080
```
You can access the sample application in the browser of host machine.

## Verify the monitoring installation

![kubectl get all](~/answer-img/get-all.png)

![kubectl get all -n monitoring](~/answer-img/get-all-monitoring.png)

![kubectl get all -n observability](~/answer-img/get-all-obserability.png)

## Setup the Jaeger and Prometheus source
![Grafana Login](~/answer-img/grafana-login.png)

![Datasource](~/answer-img/datasource.png)

## Create a Basic Dashboard
![Basic Dashboard](~/answer-img/basic-dashboard.png)

## Describe SLO/SLI
Describe, in your own words, what the SLIs are, based on an SLO of *monthly uptime* and *request response time*.

SLIs are the actual metrics of our application's performance such as actual uptime of application in a month and SLO is the predefined metrics which we expect to get over specific time.

## Creating SLI metrics.
It is important to know why we want to measure certain metrics for our customer. Describe in detail 5 metrics to measure these SLIs. 

It is important to know we have to measure certain metrics for our customer because we always watch the performance of applications to provide the best service to our customer as much as we could.
1. Request and response time of the app to know the latency
2. Application uptime over the specific time
3. CPU and memory usage of the app to check the saturation
4. Number of requests per second to the traffic of the app
5. Number of error responses to know the failure rate of the app

## Create a Dashboard to measure our SLIs

![Panels](~/answer-img/panels.png)

## Tracing our Flask App

![Jaeger](~/answer-img/jaeger.png)

 
## Report Error
*TODO:* Using the template below, write a trouble ticket for the developers, to explain the errors that you are seeing (400, 500, latency) and to let them know the file that is causing the issue also include a screenshot of the tracer span to demonstrate how we can user a tracer to locate errors easily.

TROUBLE TICKET

Name: Mongodb setup missing

Date: 20/12/2021

Subject: Database is not set up yet

Affected Area: Data Storage

Severity: High

Description: Data can not be stored.

## Creating SLIs and SLOs

We want to create an SLO guaranteeing that our application has a 99.95% uptime per month. Name four SLIs that you would use to measure the success of this SLO.

Building KPIs for our plan

Now that we have our SLIs and SLOs, create a list of 2-3 KPIs to accurately measure these metrics as well as a description of why those KPIs were chosen. We will make a dashboard for this, but first write them down here.

1. Uptime of application
2. Resources usage of application such as CPU, Memory and Disk
3. Request and response of the application 
4. Failure rate of the requests 

Final Dashboard

Create a Dashboard containing graphs that capture all the metrics of your KPIs and adequately representing your SLIs and SLOs. Include a screenshot of the dashboard here, and write a text description of what graphs are represented in the dashboard.

1. Application uptime should be watched whether the app in the cluster running proper or not.
2. Some container or service may use resource such as memory or cpu so that resource usage need to watch.
3. It is important to keep an eye on request and response of the application
4. Failure rate is needed to calculate the buffer for the gap between SLO and SLI.


  