library(shiny)

# Informa ao R que a pasta www está bem do lado dele
addResourcePath("site", "www")

ui <- fluidPage(
  tags$script(HTML("window.location.replace('site/index.html');"))
)

server <- function(input, output, session) {
}

shinyApp(ui, server)