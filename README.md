# k8s-certificates-components-exporter

A daemon checking component statuses and days left before certificates expirations and make them scrapable by prometheus.

# Metrics

```
# HELP kubernetes_ceritifiate_days_left Days left before nodes/apiservers certificates will be invalid
# TYPE kubernetes_ceritifiate_days_left gauge
kubernetes_ceritifiate_days_left{node="nodename1"} 262.0
kubernetes_ceritifiate_days_left{node="nodename2"} 242.0
kubernetes_ceritifiate_days_left{node="nodename3"} 242.0
kubernetes_ceritifiate_days_left{node="nodename4"} 242.0
kubernetes_ceritifiate_days_left{node="nodename5"} 242.0
kubernetes_ceritifiate_days_left{node="nodename6"} 251.0
kubernetes_ceritifiate_days_left{node="nodename7"} 251.0
kubernetes_ceritifiate_days_left{node="nodename8"} 251.0
# HELP kubernetes_components_statuses This will be set to 0 if components are OK, and 1 if they are not.
# TYPE kubernetes_components_statuses gauge
kubernetes_components_statuses{component="scheduler"} 0.0
kubernetes_components_statuses{component="controller-manager"} 0.0
kubernetes_components_statuses{component="etcd-0"} 0.0
kubernetes_components_statuses{component="etcd-2"} 0.0
kubernetes_components_statuses{component="etcd-1"} 0.0
```

# RBAC

```yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: resourcemonitor
  namespace: kube-system
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
   name: resource-monitor-role
rules:
 - apiGroups: ["*"]
   resources: ["nodes", "endpoints", "componentstatuses"]
   verbs: ["get", "list", "watch",]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: resource-monitor-rolebinding
  namespace: 'kube-system'
subjects:
- kind: ServiceAccount
  name: resourcemonitor
  namespace: 'kube-system'
roleRef:
  kind: ClusterRole
  name: resource-monitor-role
  apiGroup: rbac.authorization.k8s.io
```

# Deployment

```yaml
apiVersion: v1
items:
- apiVersion: extensions/v1beta1
  kind: Deployment
  metadata:
    annotations:
      deployment.kubernetes.io/revision: "1"
    labels:
      app: resourcemonitor
      version: master
    name: resourcemonitor
    namespace: kube-system
  spec:
    replicas: 1
    revisionHistoryLimit: 1
    selector:
      matchLabels:
        app: resourcemonitor
    strategy:
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 1
      type: RollingUpdate
    template:
      metadata:
        annotations:
          prometheus.io/port: "7000"
          prometheus.io/scrape: "true"
        labels:
          app: resourcemonitor
          version: master
      spec:
        automountServiceAccountToken: true
        containers:
        - image: CHANGEME:latest
          imagePullPolicy: Always
          name: resourcemonitor
          ports:
          - containerPort: 7000
            name: metrics
            protocol: TCP
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        serviceAccount: resourcemonitor
        serviceAccountName: resourcemonitor
        terminationGracePeriodSeconds: 30
kind: List
metadata:
  resourceVersion: ""
  selfLink: ""

```
## Optional ETCD certificates expiration monitoring

You can add in `deployment.yaml`:

```yaml
[snip]
          ports:
          - containerPort: 7000
            name: metrics
            protocol: TCP
          env:
          - name: ETCD
            value: "a,list,of,addresses"
[/snip]
```

The iplist in `ETCD` will be polled. The checked port will be `2379`.



# Prometheus rules

```yaml
- alert: ComponentIsInDeepShit
  expr: kubernetes_components_statuses != 0
  for: 10m
  labels:
    severity: critical
    frequency: low
  annotations:
    description: "{{ $labels.component }} is seen as unhealthy."
    summary: You need to check your components.
- alert: CertificateWillSoonExpire
  expr: kubernetes_ceritifiate_days_left < 40
  for: 10m
  labels:
    severity: critical
    frequency: low
  annotations:
    description: "{{ $labels.node }} will soon expire its certificate."
    summary: You need to check your certificates expiration date.
```

# TODO

* [ ] retrieve components ports from configmap/environment variable