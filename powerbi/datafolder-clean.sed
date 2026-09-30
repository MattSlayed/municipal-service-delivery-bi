# Git clean filter: commits the DataFolder parameter with a placeholder path, so a local
# folder path never reaches the repository. The working copy keeps its real path.
# Set-up: see "Opening the Power BI project" in README.md.
s|^(expression DataFolder = )"[^"]*"|\1"C:\\path\\to\\municipal-service-delivery-bi\\data\\processed\\"|
