library(shiny)
library(ggplot2)
library(dplyr)
library(tidyr)
library(plotly)
library(scales)
library(DT) # Load DT package for interactive tables

source("analytics.R")

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
        tabPanel(
            "Summary",
            # titlePanel(tags$h1("VirtuAnalytics")),

            # Sidebar layout with checkboxes for each rank
            sidebarLayout(
                sidebarPanel(
                    fluidRow(
                        column(
                            3,
                            actionButton("select_all_ranks", "Select All"),
                            actionButton("clear_all_ranks", "Clear All"),
                            checkboxGroupInput("ranks", "Ranks",
                                choices = ranks,
                                selected = ranks
                            ),
                        ),
                        column(
                            4,
                            # Select All / Clear All buttons for characters
                            actionButton("select_all_characters", "Select All"),
                            actionButton("clear_all_characters", "Clear All"),
                            div(class = "two-columns",
                            checkboxGroupInput("characters", "Characters",
                                choices = characters,
                                selected = characters,                                
                            ))
                        ),
                        column(4,
                            actionButton("select_all_stages", "Select All"),
                            actionButton("clear_all_stages", "Clear All"),
                            div(class="two-columns",
                            checkboxGroupInput("stages", "Stages",
                                choices = stages,
                                selected = stages
                            ))
                        )
                    ),
                ),

                # Main panel to display the bar charts
                mainPanel(
                    fluidRow(                        
                        column(4,
                            h2("Youtube Videos (Source Data)"),
                            DT::dataTableOutput("youtube_videos_table")
                        ),
                        column(8,
                    plotOutput("rankDistPlot"),
                    plotOutput("characterDistPlot"),
                    plotOutput("stageDistPlot")))
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
        tabPanel(
            "Akira",
            fluidRow(
                tags$p(paste(count_character_matches(data, "Akira"), " total matches")),
            ),
            fluidRow(                                
                column(6, DT::dataTableOutput("akira_wins_per_stage_table"),
                    DT::dataTableOutput("akira_wins_per_stage_lookup_table")
                ),
                column(6, DT::dataTableOutput("akira_wins_per_character_table")),
            )
        ),        
        tabPanel(
            "Blaze",
            fluidRow(
                tags$p(paste(count_character_matches(data, "Blaze"), " total matches")),
            ),
            fluidRow(                                
                column(6, DT::dataTableOutput("blaze_wins_per_stage_table"),
                    DT::dataTableOutput("blaze_wins_per_stage_lookup_table")
                ),
                column(6, DT::dataTableOutput("blaze_wins_per_character_table")),
            )
        ),
        tabPanel(
            "Eileen",
            fluidRow(
                tags$p(paste(count_character_matches(data, "Eileen"), " total matches")),
            ),
            fluidRow(
                column(6, DT::dataTableOutput("eileen_wins_per_stage_table"),
                DT::dataTableOutput("eileen_wins_per_stage_lookup_table")
                ),
                column(6, DT::dataTableOutput("eileen_wins_per_character_table")),
            )
        ),
        tabPanel(
            "Jacky",
            fluidRow(
                tags$p(paste(count_character_matches(data, "Jacky"), " total matches")),
            ),
            fluidRow(
                column(6, DT::dataTableOutput("jacky_wins_per_stage_table"),
                DT::dataTableOutput("jacky_wins_per_stage_lookup_table")
                ),
                column(6, DT::dataTableOutput("jacky_wins_per_character_table")),
            )
        ),        
        tabPanel(
            "Shun",
            fluidRow(
                tags$p(paste(count_character_matches(data, "Shun"), " total matches")),
            ),
            fluidRow(
                column(6, DT::dataTableOutput("shun_wins_per_stage_table"),
                DT::dataTableOutput("shun_wins_per_stage_lookup_table")
                ),
                column(6, DT::dataTableOutput("shun_wins_per_character_table")),
            )
        ),                
        tabPanel(
            "Taka",
            fluidRow(
                tags$p(paste(count_character_matches(data, "Taka"), " total matches")),
            ),
            fluidRow(
                column(6, DT::dataTableOutput("taka_wins_per_stage_table"),
                DT::dataTableOutput("taka_wins_per_stage_lookup_table")
                ),
                column(6, DT::dataTableOutput("taka_wins_per_character_table")),
            )
        )
    )
)
