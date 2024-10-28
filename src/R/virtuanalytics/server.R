library(shiny)
library(ggplot2)
library(dplyr)
library(tidyr)
library(plotly)
library(scales)
library(DT) # Load DT package for interactive tables

source("ui.R")
source("analytics.R")
source("analytics_character.R")

dict <- list(
    "Ranks" = c("English" = "Ranks", "日本語" = "段位"),
    "Stages" = c("English" = "Stages", "日本語" = "ステージ"),
    "Characters" = c("English" = "Characters", "日本語" = "キャラクター"),
    "Select All" = c("English" = "Select All", "日本語" = "すべて選択"),
    "Clear All" = c("English" = "Clear All", "日本語" = "すべてクリア"),
    "Match List" = c("English" = "Match List", "日本語" = "試合一覧"),
    "Akira" = c("English" = "Akira", "日本語" = "晶"),
    "Pai" = c("English" = "Pai", "日本語" = "パイ"),
    "Lau" = c("English" = "Lau", "日本語" = "ラウ"),
    "Wolf" = c("English" = "Wolf", "日本語" = "ウルフ"),
    "Jeffry" = c("English" = "Jeffry", "日本語" = "ジェフリー"),
    "Kage" = c("English" = "Kage", "日本語" = "影"),
    "Sarah" = c("English" = "Sarah", "日本語" = "サラ"),
    "Jacky" = c("English" = "Jacky", "日本語" = "ジャッキー"),
    "Shun" = c("English" = "Shun", "日本語" = "舜 帝"),
    "Lion" = c("English" = "Lion", "日本語" = "リオン"),
    "Aoi" = c("English" = "Aoi", "日本語" = "葵"),
    "LeiFei" = c("English" = "Lei-Fei", "日本語" = "雷 飛"),
    "Vanessa" = c("English" = "Vanessa", "日本語" = "ベネッサ"),
    "Brad" = c("English" = "Brad", "日本語" = "ブラッド"),
    "Goh" = c("English" = "Goh", "日本語" = "剛"),
    "Eileen" = c("English" = "Eileen", "日本語" = "アイリーン"),
    "Blaze" = c("English" = "Blaze", "日本語" = "エル・ブレイズ"),
    "Taka" = c("English" = "Taka", "日本語" = "鷹嵐"),
    "Jean" = c("English" = "Jean", "日本語" = "ジャン"),
    "Video Search" = c("English" = "Video Search", "日本語" = "検索")
)

create_character_tables <- function(output, data, character_name) {
    l_character_name <- tolower(character_name)


    # Wins per Character Table
    output[[paste0(l_character_name, "_wins_per_character_table")]] <- DT::renderDataTable({
        datatable(character_matchup_win_table(data, character_name), options = list(
            pageLength = 20,
            paging = FALSE,
            searching = FALSE
        )) %>%
            formatPercentage("Win.Percentage", digits = 0) %>%
            formatRound("p_value", digits = 3) %>%
            formatStyle(
                "p_value",
                backgroundColor = styleInterval(c(0.05), c("yellow", ""))
            )
    })

    # Wins per Stage Table
    output[[paste0(l_character_name, "_wins_per_stage_table")]] <- DT::renderDataTable({
        datatable(win_percentages_per_character(data, character_name), options = list(
            pageLength = 20,
            paging = FALSE,
            searching = FALSE
        )) %>%
            formatPercentage("Win.Percentage", digits = 0) %>%
            formatRound("p_value", digits = 3) %>%
            formatStyle(
                "p_value",
                backgroundColor = styleInterval(c(0.05), c("yellow", ""))
            )
    })


    return(1)

    # Match Wins per Stage Lookup Table
    output[[paste0(l_character_name, "_match_wins_per_stage_lookup_table")]] <- DT::renderDataTable({
        char_data <- matches_won_per_stage_per_character(data, character_name)

        datatable(char_data, options = list(
            dom = "t",
            paging = FALSE,
            searching = FALSE
        )) %>%
            formatRound(columns = c(1:ncol(char_data)), digits = 3) %>%
            formatStyle(
                columns = names(char_data),
                backgroundColor = styleInterval(c(0.05), c("yellow", ""))
            )
    })

    # Wins per Stage Lookup Table
    output[[paste0(l_character_name, "_wins_per_stage_lookup_table")]] <- DT::renderDataTable({
        char_data <- rounds_won_per_stage_per_character_lookup(data, character_name)

        datatable(char_data, options = list(
            dom = "t", # Only show the table body, no footer
            paging = FALSE, # Disable pagination
            searching = FALSE # Disable the search box
        )) %>%
            formatRound(columns = c(1:ncol(char_data)), digits = 3) %>%
            formatStyle(
                columns = names(char_data),
                backgroundColor = styleInterval(c(0.05), c("yellow", "")) # Highlight cells <= 0.05
            )
    })
}

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

    selected_language <- reactive({
        input$language
    })

    output$MatchList <- renderText(dict[["Match List"]][[selected_language()]])
    output$VideoSearch <- renderText(dict[["Video Search"]][[selected_language()]])
    output$Ranks <- renderText(dict[["Ranks"]][[selected_language()]])
    output$Stages <- renderText(dict[["Stages"]][[selected_language()]])
    output$Characters <- renderText(dict[["Characters"]][[selected_language()]])
    output$SelectAllStages <- renderText(dict[["Select All"]][[selected_language()]])
    output$ClearAllStages <- renderText(dict[["Clear All"]][[selected_language()]])
    output$SelectAllCharacters <- renderText(dict[["Select All"]][[selected_language()]])
    output$ClearAllCharacters <- renderText(dict[["Clear All"]][[selected_language()]])
    output$SelectAllRanks <- renderText(dict[["Select All"]][[selected_language()]])
    output$ClearAllRanks <- renderText(dict[["Clear All"]][[selected_language()]])
    
    output$AkiraButton <- renderText(dict[["Akira"]][[selected_language()]])
    output$BlazeButton <- renderText(dict[["Blaze"]][[selected_language()]])
    output$EileenButton <- renderText(dict[["Eileen"]][[selected_language()]])    
    output$PaiButton <- renderText(dict[["Pai"]][[selected_language()]])
    output$LauButton <- renderText(dict[["Lau"]][[selected_language()]])
    output$WolfButton <- renderText(dict[["Wolf"]][[selected_language()]])
    output$JeffryButton <- renderText(dict[["Jeffry"]][[selected_language()]])
    output$KageButton <- renderText(dict[["Kage"]][[selected_language()]])
    output$SarahButton <- renderText(dict[["Sarah"]][[selected_language()]])
    output$JackyButton <- renderText(dict[["Jacky"]][[selected_language()]])
    output$ShunButton <- renderText(dict[["Shun"]][[selected_language()]])
    output$LionButton <- renderText(dict[["Lion"]][[selected_language()]])
    output$AoiButton <- renderText(dict[["Aoi"]][[selected_language()]])
    output$LeiFeiButton <- renderText(dict[["LeiFei"]][[selected_language()]])
    output$VanessaButton <- renderText(dict[["Vanessa"]][[selected_language()]])
    output$BradButton <- renderText(dict[["Brad"]][[selected_language()]])
    output$GohButton <- renderText(dict[["Goh"]][[selected_language()]])
    output$TakaButton <- renderText(dict[["Taka"]][[selected_language()]])
    output$JeanButton <- renderText(dict[["Jean"]][[selected_language()]])


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
            mutate(character = sapply(character, function(char) dict[[char]][[input$language]])) %>%
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

    create_character_tables(output, data, "Akira")
    create_character_tables(output, data, "Aoi")
    create_character_tables(output, data, "Brad")
    create_character_tables(output, data, "Eileen")
    create_character_tables(output, data, "Blaze")
    create_character_tables(output, data, "Goh")
    create_character_tables(output, data, "Jean")
    create_character_tables(output, data, "Jacky")
    create_character_tables(output, data, "Jeffry")
    create_character_tables(output, data, "Kage")
    create_character_tables(output, data, "Lau")
    create_character_tables(output, data, "Lei Fei")
    create_character_tables(output, data, "Lion")
    create_character_tables(output, data, "Pai")
    create_character_tables(output, data, "Sarah")
    create_character_tables(output, data, "Shun")
    create_character_tables(output, data, "Taka")
    create_character_tables(output, data, "Vanessa")
    create_character_tables(output, data, "Wolf")
}
