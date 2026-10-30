{{/*
Nom du chart, tronqué à 63 caractères (limite des noms DNS Kubernetes).
*/}}
{{- define "kubesentinel.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Nom complet, préfixe de toutes les ressources.
Release "kubesentinel" → "kubesentinel" ; release "demo" → "demo-kubesentinel".
*/}}
{{- define "kubesentinel.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Labels de sélection : ils lient un Deployment/StatefulSet et un Service à leurs pods.
Ils doivent rester STABLES (le selector d'un Deployment est immuable).
Usage : include "kubesentinel.selectorLabels" (dict "ctx" . "component" "api")
*/}}
{{- define "kubesentinel.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kubesentinel.name" .ctx }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Labels communs à poser sur toutes les ressources (metadata.labels).
Usage : include "kubesentinel.labels" (dict "ctx" . "component" "api")
*/}}
{{- define "kubesentinel.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .ctx.Chart.Name .ctx.Chart.Version }}
{{ include "kubesentinel.selectorLabels" . }}
app.kubernetes.io/version: {{ .ctx.Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .ctx.Release.Service }}
app.kubernetes.io/part-of: kubesentinel
{{- end }}

{{/*
Nom des ressources PostgreSQL (StatefulSet, Service). Le Service porte ce nom :
c'est donc aussi le nom DNS que l'API utilise comme DB_HOST.
*/}}
{{- define "kubesentinel.postgresql.fullname" -}}
{{- printf "%s-postgresql" (include "kubesentinel.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
