@echo off
echo Adding files to git...
git add .
echo Committing changes...
git commit -m "Add comprehensive Intervention Reports module

- Created complete reports app with models, serializers, views
- Added ReportTemplate, InterventionReport, ReportMedia, ReportSignature models
- Implemented REST API endpoints for all report operations
- Created Django templates for reports interface
- Added reports navigation to base template and home page
- Updated settings and requirements for reports functionality
- Added support for dynamic forms, media uploads, and digital signatures"
echo Pushing to GitHub...
git push origin main
echo Done!
pause
