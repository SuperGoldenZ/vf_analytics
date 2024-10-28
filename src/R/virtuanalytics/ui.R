library(shiny)
library(ggplot2)
library(dplyr)
library(tidyr)
library(plotly)
library(scales)
library(DT) # Load DT package for interactive tables

source("analytics.R")
source("analytics_character.R")

characters <- unique(data$Player.1.Character)

generate_character_tab <- function(character) {
    tabPanel(
        uiOutput(paste0(character,"Button")),
        fluidRow(
            tags$p(paste(count_character_matches(data, character), " total matches"))
        ),
        fluidRow(
            column(
                6,
                DT::dataTableOutput(paste0(tolower(character), "_wins_per_stage_table")),
                DT::dataTableOutput(paste0(tolower(character), "_match_wins_per_stage_lookup_table")),
                DT::dataTableOutput(paste0(tolower(character), "_wins_per_stage_lookup_table"))
            ),
            column(
                6,
                DT::dataTableOutput(paste0(tolower(character), "_wins_per_character_table"))
            )
        )
    )
}

# Define UI
ui <- fluidPage(
    tags$head(
        tags$title("VirtuAnalytics"),
        tags$style(HTML("
      @import url('https://fonts.googleapis.com/css2?family=Brush+Script+MT&display=swap');

      h1 {
        font-family: 'Caveat Brush', cursive;
        font-size: 50px;
        background: -webkit-linear-gradient(top, white, yellow, red, gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: left;
        background-color: #421301;
      }

        .two-columns .checkbox {
          width: 50%;
          float: left;
        }

        .dataTable {
        font-size: 12px;  /* Change this value to adjust the font size */
      }

      /*body {
        background-color: #9c7c70;
      }*/
    "))
    ),
    navbarPage(
        "VirtuaAnalytics",
        
        header = tagList(
            div(
                radioButtons(
                    "language",
                    label = NULL, # No label to minimize space
                    choices = c("English", "日本語"),
                    selected = "English",
                    inline = TRUE
                ),
                style = "position: relative; float: right; margin-right: 20px;margin-top: -50px; z-index: 9999; "
            )
        ),
        tabPanel(
            uiOutput("VideoSearch"),
            # titlePanel(tags$h1("VirtuAnalytics")),

            # Sidebar layout with checkboxes for each rank
            sidebarLayout(
                sidebarPanel(
                    fluidRow(
                        column(
                            3,
                            actionButton("select_all_ranks", uiOutput("SelectAllRanks")),
                            actionButton("clear_all_ranks", uiOutput("ClearAllRanks")),
                            checkboxGroupInput("ranks", uiOutput("Ranks"),
                                choices = ranks,
                                selected = ranks
                            ),
                        ),
                        column(
                            4,
                            # Select All / Clear All buttons for characters
                            actionButton("select_all_characters", uiOutput("SelectAllCharacters")),
                            actionButton("clear_all_characters", uiOutput("ClearAllCharacters")),
                            div(
                                class = "two-columns",
                                checkboxGroupInput("characters", uiOutput("Characters"),
                                    choices = characters,
                                    selected = characters,
                                )
                            )
                        ),
                        column(
                            4,
                            actionButton("select_all_stages", uiOutput("SelectAllStages")),
                            actionButton("clear_all_stages", uiOutput("ClearAllStages")),
                            div(
                                class = "two-columns",
                                checkboxGroupInput("stages", uiOutput("Stages"),
                                    choices = stages,
                                    selected = stages
                                )
                            )
                        )
                    ),
                ),

                # Main panel to display the bar charts
                mainPanel(
                    fluidRow(
                        column(
                            4,
                            h2(uiOutput("MatchList")),
                            DT::dataTableOutput("youtube_videos_table")
                        ),
                        column(
                            8,
                            plotOutput("rankDistPlot"),
                            plotOutput("characterDistPlot"),
                            plotOutput("stageDistPlot")
                        )
                    )
                )
            ),
            hr(style = "border-top: 3px solid #421301; margin-top: 30px; margin-bottom: 30px;"),
            fluidRow(
                # column(6,tableOutput('win_rate_table')),
                # column(6,tableOutput('character_matchup_table')),
                column(6, DT::dataTableOutput("win_rate_table")),
                column(6, DT::dataTableOutput("character_matchup_table")),
            )
        ),
        # lapply(characters, generate_character_tab),
        generate_character_tab("Akira"),
        generate_character_tab("Aoi"),
        generate_character_tab("Brad"),
        generate_character_tab("Eileen"),
        generate_character_tab("Blaze"),
        generate_character_tab("Goh"),
        generate_character_tab("Jean"),
        generate_character_tab("Jacky"),
        generate_character_tab("Jeffry"),
        generate_character_tab("Kage"),
        generate_character_tab("Lau"),
        generate_character_tab("LeiFei"),
        generate_character_tab("Lion"),
        generate_character_tab("Pai"),
        generate_character_tab("Sarah"),
        generate_character_tab("Shun"),
        generate_character_tab("Taka"),
        generate_character_tab("Vanessa"),
        generate_character_tab("Wolf"),
    )
)
