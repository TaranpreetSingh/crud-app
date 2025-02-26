{{/* Common labels */}}
{{- define "crud-app.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ .Release.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/* Selector labels */}}
{{- define "crud-app.selectorLabels" -}}
app.kubernetes.io/name: {{ .Release.Name }}-crud-app
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
