library(shiny)
library(ggplot2)
library(dplyr)
library(tidyr)
library(plotly)
library(scales)
library(DT) # Load DT package for interactive tables

source("ui.R")

# Define server logic
server <- function(input, output, session) {
    # Select All / Clear All buttons for ranks
    observeEvent(input$select_all_ranks, {
        updateCheckboxGroupInput(session, "ranks", selected = ranks)
    })

    observeEvent(input$clear_all_ranks, {
        updateCheckboxGroupInput(session, "ranks", selected = character(0))
    })

    # Select All / Clear All buttons for characters
    observeEvent(input$select_all_characters, {
        updateCheckboxGroupInput(session, "characters", selected = characters)
    })

    observeEvent(input$clear_all_characters, {
        updateCheckboxGroupInput(session, "characters", selected = character(0))
    })

    # Select All / Clear All buttons for stages
    observeEvent(input$select_all_stages, {
        updateCheckboxGroupInput(session, "stages", selected = stages)
    })

    observeEvent(input$clear_all_stages, {
        updateCheckboxGroupInput(session, "stages", selected = character(0))
    })

    # Reactive data filtering based on selected ranks
    filtered_data <- reactive({
        data_combined %>%
            filter(player_rank %in% input$ranks) %>%
            filter(character %in% input$characters) %>%
            filter(stage %in% input$stages)
    })

    youtube_video_data <- reactive({
        match_data %>%
            filter(Player.1.Rank %in% input$ranks | Player.2.Rank %in% input$ranks) %>%
            filter(Player.1.Character %in% input$characters | Player.2.Character %in% input$characters) %>%
            filter(Stage %in% input$stages) %>%
            mutate(Stage = Stage, Desc = paste("Lv", Player.1.Rank, " ", Player.1.Character, " vs Lv", Player.2.Rank, " ", Player.2.Character), Link = Youtube.Link) %>%
            select(Stage, Desc, Link)
    })

    # Calculate total number of samples
    total_samples <- reactive({
        nrow(filtered_data()) # Get the number of rows in the data
    })

    # Rank distribution plot
    output$rankDistPlot <- renderPlot({
        rank_counts <- filtered_data() %>%
            select(player_rank) %>%
            pivot_longer(cols = everything(), names_to = "Player", values_to = "Rank") %>%
            count(Rank)

        ggplot(rank_counts, aes(x = Rank, y = n, fill = Rank)) +
            geom_bar(stat = "identity") +
            labs(title = paste("Rank Distribution (", comma(total_samples() / 4), " matches)"), x = "Rank", y = "Count") +
            theme_minimal() +
            theme(plot.margin = margin(b = 15))
    })

    # Character distribution plot
    output$characterDistPlot <- renderPlot({
        character_counts <- filtered_data() %>%
            select(character) %>%
            pivot_longer(cols = everything(), names_to = "Player", values_to = "Character") %>%
            count(Character)

        ggplot(character_counts, aes(x = Character, y = n, fill = Character)) +
            geom_bar(stat = "identity") +
            labs(title = paste("Character Distribution (", comma(total_samples() / 4), " matches)"), x = "Character", y = "Count") +
            theme_minimal() +
            theme(axis.text.x = element_text(angle = 45, hjust = 1), plot.margin = margin(b = 15))
    })

    # Character distribution plot
    output$stageDistPlot <- renderPlot({
        stage_counts <- filtered_data() %>%
            select(stage) %>%
            pivot_longer(cols = everything(), values_to = "Stage") %>%
            count(Stage)

        ggplot(stage_counts, aes(x = Stage, y = n, fill = Stage)) +
            geom_bar(stat = "identity") +
            labs(title = paste("Stage Distribution (", comma(total_samples() / 4), " matches)"), x = "Stage", y = "Count") +
            theme_minimal() +
            theme(axis.text.x = element_text(angle = 45, hjust = 1), plot.margin = margin(b = 15))
    })

    # Calculate and render overall win rates per character
    # output$win_rate_table <- renderTable(win_percentage_table)

    # output$character_matchup_table <- renderTable(character_matchup)
    output$youtube_videos_table <- DT::renderDataTable({
        datatable(youtube_video_data(), escape = FALSE)
    })

    output$win_rate_table <- DT::renderDataTable({
        datatable(win_percentage_table, options = list(pageLength = 20, paging = FALSE, searching = FALSE, dom = "t")) %>% formatPercentage("Win_Percentage", digits = 0)
    })
    output$character_matchup_table <- DT::renderDataTable({
        datatable(character_matchup, options = list(paging = FALSE, searching = FALSE)) %>% formatPercentage("Win_Percentage", digits = 0)
    })

    output$blaze_wins_per_stage_lookup_table <- DT::renderDataTable({
        blaze_data <- rounds_won_per_stage_per_character_lookup(data, "Blaze")

        datatable(blaze_data, options = list(
            dom = "t", # Only show the table body, no footer
            paging = FALSE, # Disable pagination
            searching = FALSE # Disable the search box
        )) %>%
            formatRound(columns = c(1:ncol(blaze_data)), digits = 3) %>%
            formatStyle(
                columns = names(blaze_data), # Specify the columns you want to style
                backgroundColor = styleInterval(c(0.05), c("yellow", "")) # Highlight cells <= 0.05
            )
    })

    output$eileen_wins_per_stage_lookup_table <- DT::renderDataTable({
        eileen_data <- rounds_won_per_stage_per_character_lookup(data, "Eileen")

        datatable(eileen_data, options = list(
            dom = "t", # Only show the table body, no footer
            paging = FALSE, # Disable pagination
            searching = FALSE # Disable the search box
        )) %>%
            formatRound(columns = c(1:ncol(eileen_data)), digits = 3) %>%
            formatStyle(
                columns = names(eileen_data), # Specify the columns you want to style
                backgroundColor = styleInterval(c(0.05), c("yellow", "")) # Highlight cells <= 0.05
            )
    })

    output$taka_wins_per_stage_lookup_table <- DT::renderDataTable({
        taka_data <- rounds_won_per_stage_per_character_lookup(data, "Taka")

        datatable(taka_data, options = list(
            dom = "t", # Only show the table body, no footer
            paging = FALSE, # Disable pagination
            searching = FALSE # Disable the search box
        )) %>%
            formatRound(columns = c(1:ncol(taka_data)), digits = 3) %>%
            formatStyle(
                columns = names(taka_data), # Specify the columns you want to style
                backgroundColor = styleInterval(c(0.05), c("yellow", "")) # Highlight cells <= 0.05
            )
    })

    output$blaze_wins_per_stage_table <- DT::renderDataTable({
        datatable(win_percentages_per_character(data, "Blaze"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$blaze_wins_per_character_table <- DT::renderDataTable({
        datatable(character_matchup_win_table(data, "Blaze"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$eileen_wins_per_stage_table <- DT::renderDataTable({
        datatable(win_percentages_per_character(data, "Eileen"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$eileen_wins_per_character_table <- DT::renderDataTable({
        datatable(character_matchup_win_table(data, "Eileen"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })


    output$taka_wins_per_stage_table <- DT::renderDataTable({
        datatable(win_percentages_per_character(data, "Taka"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$taka_wins_per_character_table <- DT::renderDataTable({
        datatable(character_matchup_win_table(data, "Taka"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    ########
    # Jacky
    ########
    output$jacky_wins_per_stage_table <- DT::renderDataTable({
        datatable(win_percentages_per_character(data, "Jacky"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$jacky_wins_per_character_table <- DT::renderDataTable({
        datatable(character_matchup_win_table(data, "Jacky"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$jacky_wins_per_stage_lookup_table <- DT::renderDataTable({
        jacky_data <- rounds_won_per_stage_per_character_lookup(data, "Jacky")

        datatable(jacky_data, options = list(
            dom = "t", # Only show the table body, no footer
            paging = FALSE, # Disable pagination
            searching = FALSE # Disable the search box
        )) %>%
            formatRound(columns = c(1:ncol(jacky_data)), digits = 3) %>%
            formatStyle(
                columns = names(jacky_data), # Specify the columns you want to style
                backgroundColor = styleInterval(c(0.05), c("yellow", "")) # Highlight cells <= 0.05
            )
    })

    ########
    # Akira
    ########
    output$akira_wins_per_stage_table <- DT::renderDataTable({
        datatable(win_percentages_per_character(data, "Akira"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$akira_wins_per_character_table <- DT::renderDataTable({
        datatable(character_matchup_win_table(data, "Akira"), options = list(pageLength = 20, paging = FALSE)) %>% formatPercentage("Win.Percentage", digits = 0)
    })

    output$akira_wins_per_stage_lookup_table <- DT::renderDataTable({
        Akira_data <- rounds_won_per_stage_per_character_lookup(data, "Akira")

        datatable(Akira_data, options = list(
            dom = "t", # Only show the table body, no footer
            paging = FALSE, # Disable pagination
            searching = FALSE # Disable the search box
        )) %>%
            formatRound(columns = c(1:ncol(Akira_data)), digits = 3) %>%
            formatStyle(
                columns = names(Akira_data), # Specify the columns you want to style
                backgroundColor = styleInterval(c(0.05), c("yellow", "")) # Highlight cells <= 0.05
            )
    })
}
