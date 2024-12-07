library(shiny)

source("analytics_character.R")
source("ui.R")
source("server.R")

options(shiny.port = 8080)

# Run the application
shinyApp(ui = ui, server = server)
