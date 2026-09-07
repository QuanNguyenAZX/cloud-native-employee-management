{{- define "employee-management.namespace" -}}
{{- .Values.namespace.name | default "employee-management" -}}
{{- end -}}

{{- define "employee-management.name" -}}
employee-management
{{- end -}}

{{- define "employee-management.backendName" -}}
employee-backend
{{- end -}}

{{- define "employee-management.frontendName" -}}
employee-frontend
{{- end -}}

{{- define "employee-management.postgresName" -}}
postgres
{{- end -}}

{{- define "employee-management.minioName" -}}
minio
{{- end -}}

{{- define "employee-management.labels" -}}
app.kubernetes.io/name: {{ include "employee-management.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "employee-management.backendLabels" -}}
app.kubernetes.io/name: {{ include "employee-management.backendName" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "employee-management.frontendLabels" -}}
app.kubernetes.io/name: {{ include "employee-management.frontendName" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "employee-management.postgresLabels" -}}
app.kubernetes.io/name: {{ include "employee-management.postgresName" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "employee-management.minioLabels" -}}
app.kubernetes.io/name: {{ include "employee-management.minioName" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
