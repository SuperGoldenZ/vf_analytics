win_percentages_per_character <- function(data, character_name) {
    stage_type_lookup <- data.frame(
        Stage = c(
            "Deep Mountain", "Palace", "City", "Ruins", "Arena", "Waterfalls",
            "Broken House", "Grassland", "Aurora", "Island", "Statues",
            "Terrace", "Snow Mountain", "Training Room", "Shrine", "Temple",
            "River", "Sumo Ring", "Genesis", "Great Wall"
        ),
        Stage.Type = c(
            "Rectangle", "Rectangle", "Full Fence", "Full Fence", "Octagon", "Octagon",
            "Breakable Full Fence", "Breakable Full Fence", "Breakable Half Fence",
            "Breakable Half Fence", "Half Fence", "Half Fence", "Full Fence and Open",
            "Full Fence and Open", "Low Fence", "Low Fence", "Open", "Open",
            "Single Wall", "Single Wall"
        )
    )

    # Add Stage Type to data based on the lookup
    stage_data <- data %>%
        left_join(stage_type_lookup, by = "Stage")

    # Filter for matches where Blaze is one of the players, but not both
    blaze_data <- stage_data %>%
        filter((Player.1.Character == character_name & Player.2.Character != character_name) |
            (Player.2.Character == character_name & Player.1.Character != character_name))

    # Determine the winner of the match (the character that won the last round)
    match_winners <- blaze_data %>%
        group_by(Match.ID) %>%
        filter(round_number == max(round_number)) %>%
        mutate(Winner_Character = ifelse(Winning.Player.Number == 1, Player.1.Character, Player.2.Character)) %>%
        select(Match.ID, Winner_Character, Stage.Type)

    # Total number of matches Blaze played in each stage category
    blaze_played_in_stage <- blaze_data %>%
        group_by(Match.ID, Stage.Type) %>%
        summarise(Total_Matches = n_distinct(Match.ID), .groups = "drop") %>%
        group_by(Stage.Type) %>%
        summarise(Total_Matches = sum(Total_Matches), .groups = "drop")

    # Total number of matches Blaze won in each stage category
    blaze_wins <- match_winners %>%
        filter(Winner_Character == character_name) %>%
        group_by(Stage.Type) %>%
        summarise(Matches_Won = n(), .groups = "drop")

    # Merge total matches and matches won, and calculate win percentage
    blaze_win_percentage <- blaze_played_in_stage %>%
        left_join(blaze_wins, by = "Stage.Type") %>%
        mutate(
            Matches_Won = ifelse(is.na(Matches_Won), 0, Matches_Won), # Handle cases with no wins
            Win_Percentage = (Matches_Won / Total_Matches) # Calculate win percentage
        ) %>%
        arrange(desc(Win_Percentage)) # Sort by win percentage in descending order

    blaze_win_percentage$p_value <- NA

    # Rename columns for clarity
    blaze_win_percentage <- blaze_win_percentage %>%
        rename(
            Stage.Category = Stage.Type,
            Matches.Won = Matches_Won,
            Total.Matches = Total_Matches,
            Win.Percentage = Win_Percentage
        )

    for (stage in unique(data$Stage)) {
        rounds_won_specific <- rounds_won_per_stage_per_character(data, character_name, stage)
        rounds_won_other <- rounds_won_per_other_stages_per_character(data, character_name, stage)

        t_test_result <- t.test(rounds_won_specific, rounds_won_other)

        blaze_win_percentage$p_value[blaze_win_percentage$Stage.Category == get_stage_type(stage, stage_type_lookup)] <- t_test_result$p.value
    }

    return(blaze_win_percentage)
}

get_stage_type <- function(stage_name, lookup_table) {
    result <- lookup_table %>%
        filter(Stage == stage_name) %>%
        select(Stage.Type) %>%
        pull() # Extract the value as a vector

    return(result)
}

rounds_won_per_stage_per_character <- function(data, character_name, stage_name) {
    stage_type_lookup <- data.frame(
        Stage = c(
            "Deep Mountain", "Palace", "City", "Ruins", "Arena", "Waterfalls",
            "Broken House", "Grassland", "Aurora", "Island", "Statues",
            "Terrace", "Snow Mountain", "Training Room", "Shrine", "Temple",
            "River", "Sumo Ring", "Genesis", "Great Wall"
        ),
        Stage.Type = c(
            "Rectangle", "Rectangle", "Full Fence", "Full Fence", "Octagon", "Octagon",
            "Breakable Full Fence", "Breakable Full Fence", "Breakable Half Fence",
            "Breakable Half Fence", "Half Fence", "Half Fence", "Full Fence and Open",
            "Full Fence and Open", "Low Fence", "Low Fence", "Open", "Open",
            "Single Wall", "Single Wall"
        )
    )

    # Add Stage Type to data based on the lookup
    stage_data <- data %>%
        left_join(stage_type_lookup, by = "Stage") %>%
        filter(Stage.Type == get_stage_type(stage_name, stage_type_lookup))

    # Filter for matches where Blaze is one of the players, but not both
    character_wins <- stage_data %>%
        filter((Player.1.Character == character_name & Player.2.Character != character_name) |
            (Player.2.Character == character_name & Player.1.Character != character_name)) %>%
        filter((Player.1.Character == character_name & Winning.Player.Number == 1) |
            (Player.2.Character == character_name & Winning.Player.Number == 2))

    rounds_won_summary <- character_wins %>%
        group_by(Match.ID, Stage) %>%
        summarise(Rounds.Won = n(), .groups = "drop") %>%
        arrange(desc(Rounds.Won)) %>%
        pull(Rounds.Won)

    return(rounds_won_summary)
}

rounds_won_per_other_stages_per_character <- function(data, character_name, stage_name) {
    stage_type_lookup <- data.frame(
        Stage = c(
            "Deep Mountain", "Palace", "City", "Ruins", "Arena", "Waterfalls",
            "Broken House", "Grassland", "Aurora", "Island", "Statues",
            "Terrace", "Snow Mountain", "Training Room", "Shrine", "Temple",
            "River", "Sumo Ring", "Genesis", "Great Wall"
        ),
        Stage.Type = c(
            "Rectangle", "Rectangle", "Full Fence", "Full Fence", "Octagon", "Octagon",
            "Breakable Full Fence", "Breakable Full Fence", "Breakable Half Fence",
            "Breakable Half Fence", "Half Fence", "Half Fence", "Full Fence and Open",
            "Full Fence and Open", "Low Fence", "Low Fence", "Open", "Open",
            "Single Wall", "Single Wall"
        )
    )

    # Add Stage Type to data based on the lookup
    stage_data <- data %>%
        left_join(stage_type_lookup, by = "Stage") %>%
        filter(Stage.Type != get_stage_type(stage_name, stage_type_lookup))

    # Filter for matches where Blaze is one of the players, but not both
    character_wins <- stage_data %>%
        filter((Player.1.Character == character_name & Player.2.Character != character_name) |
            (Player.2.Character == character_name & Player.1.Character != character_name)) %>%
        filter((Player.1.Character == character_name & Winning.Player.Number == 1) |
            (Player.2.Character == character_name & Winning.Player.Number == 2))

    rounds_won_summary <- character_wins %>%
        group_by(Match.ID, Stage) %>%
        summarise(Rounds.Won = n(), .groups = "drop") %>%
        arrange(desc(Rounds.Won)) %>%
        pull(Rounds.Won)

    return(rounds_won_summary)
}

character_matchup_win_table <- function(data, character_name) {
    # Filter out matches where both players are the same character
    matchup_data <- data %>%
        filter(Player.1.Character != Player.2.Character) %>%
        filter(Player.1.Character == character_name | Player.2.Character == character_name) %>%
        group_by(Match.ID) %>%
        filter(round_number == max(round_number))

    # Identify the winner of the match by the last round
    match_winners <- matchup_data %>%
        mutate(Winner_Character = ifelse(Winning.Player.Number == 1, Player.1.Character, Player.2.Character)) %>%
        mutate(Loser_Character = ifelse(Winning.Player.Number == 2, Player.1.Character, Player.2.Character)) %>%
        select(Match.ID, Player.1.Character, Player.2.Character, Winner_Character, Loser_Character)

    # Create two perspectives for every matchup: one with Player 1 as main character, and one with Player 2 as main character
    matchups_player1 <- match_winners %>%
        mutate(
            Main_Character = Player.1.Character,
            Opponent_Character = Player.2.Character,
            Main_Winner = (Winner_Character == character_name)
        )

    matchups_player2 <- match_winners %>%
        mutate(
            Main_Character = Player.2.Character,
            Opponent_Character = Player.1.Character,
            Main_Winner = (Winner_Character == character_name)
        )

    # Combine both perspectives into a single dataset
    full_matchup_data <- bind_rows(matchups_player1, matchups_player2) %>%
        filter(Main_Character == character_name)

    # print(full_matchup_data)

    # Summarize the results: count total matches and wins for each character-opponent pairing
    character_matchup <- full_matchup_data %>%
        group_by(Main_Character, Opponent_Character) %>%
        summarise(
            Total.Matches = n(),
            Wins_By_Main_Character = sum(Main_Winner),
            Win.Percentage = (Wins_By_Main_Character / Total.Matches),
            .groups = "drop"
        ) %>%
        arrange(desc(Win.Percentage))

    character_matchup$p_value <- NA
    return(character_matchup)
}

csv_filename <- "vf_match_data_20241022.csv"

# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Check if a file name was provided
# if (length(args) == 0) {
# stop("Error: No CSV file provided. Please provide the CSV file as an argument.")
# }

# Assign the first argument to a variable as the filename
if (length(args) > 0) {
    csv_filename <- args[1]
}

# Check if the file exists
if (!file.exists(csv_filename)) {
    stop(paste("Error: File", csv_filename, "not found. Please check the file path and try again."))
}


# Read the CSV file
data <- read.csv(csv_filename)

match_data <- data %>%
    filter(as.numeric(Player.1.Rank) >= 40 & as.numeric(Player.2.Rank) >= 40 & round_number == 0)

ranks <- sort(unique(as.numeric(c(match_data$Player.1.Rank, match_data$Player.2.Rank))))
characters <- sort(unique(c(match_data$Player.1.Character, match_data$Player.2.Character)))
stages <- sort(unique(c(match_data$Stage)))

# Combine Player 1 and Player 2 ranks and characters into one column each
data_combined <- match_data %>%
    pivot_longer(cols = c(Player.1.Rank, Player.2.Rank), names_to = "Player", values_to = "player_rank") %>%
    pivot_longer(cols = c(Player.1.Character, Player.2.Character), names_to = "PlayerCharacter", values_to = "character") %>%
    pivot_longer(cols = c(Stage), names_to = "Stage", values_to = "stage") %>%
    select(-Player, -PlayerCharacter, -Stage)

match_data$Youtube.Link <- paste0("<a href='", match_data$Youtube.Link, "' target='_blank'>Open</a>")


############################ 3
# Identify the winner for each match by the last round played in that match
match_winners <- data %>%
    group_by(Match.ID) %>%
    filter(round_number == max(round_number)) %>% # Get the last round of each match
    mutate(Winner_Character = ifelse(Winning.Player.Number == 1, Player.1.Character, Player.2.Character)) %>%
    select(Match.ID, Player.1.Character, Player.2.Character, Winner_Character)

# Calculate total number of matches each character participated in
total_matches <- match_winners %>%
    select(Match.ID, Player.1.Character, Player.2.Character) %>%
    pivot_longer(cols = c(Player.1.Character, Player.2.Character), names_to = "Player", values_to = "Character") %>%
    group_by(Character) %>%
    summarise(Total_Matches = n(), .groups = "drop")

# Calculate total number of wins for each character
win_counts <- match_winners %>%
    group_by(Winner_Character) %>%
    summarise(Total_Wins = n(), .groups = "drop")

# Merge total matches and win counts to calculate win percentage
win_percentage_table <- total_matches %>%
    left_join(win_counts, by = c("Character" = "Winner_Character")) %>%
    mutate(
        Total_Wins = ifelse(is.na(Total_Wins), 0, Total_Wins), # Handle characters with zero wins
        Win_Percentage = (Total_Wins / Total_Matches)
    ) %>%
    arrange(desc(Win_Percentage)) # Sort by win percentage in descending order

#################################
# Filter out matches where both players are the same character
matchup_data <- data %>%
    filter(Player.1.Character != Player.2.Character)

# Identify the winner of the match by the last round
match_winners <- matchup_data %>%
    group_by(Match.ID) %>%
    filter(round_number == max(round_number)) %>%
    mutate(Winner_Character = ifelse(Winning.Player.Number == 1, Player.1.Character, Player.2.Character)) %>%
    select(Match.ID, Player.1.Character, Player.2.Character, Winner_Character)

# Create two perspectives for every matchup: one with Player 1 as main character, and one with Player 2 as main character
matchups_player1 <- match_winners %>%
    mutate(
        Main_Character = Player.1.Character,
        Opponent_Character = Player.2.Character,
        Main_Winner = (Winner_Character == Player.1.Character)
    )

matchups_player2 <- match_winners %>%
    mutate(
        Main_Character = Player.2.Character,
        Opponent_Character = Player.1.Character,
        Main_Winner = (Winner_Character == Player.2.Character)
    )

# Combine both perspectives into a single dataset
full_matchup_data <- bind_rows(matchups_player1, matchups_player2)

# Summarize the results: count total matches and wins for each character-opponent pairing
character_matchup <- full_matchup_data %>%
    group_by(Main_Character, Opponent_Character) %>%
    summarise(
        Total_Matches = n(),
        Wins_By_Main_Character = sum(Main_Winner),
        Win_Percentage = (Wins_By_Main_Character / Total_Matches),
        .groups = "drop"
    ) %>%
    arrange(desc(Total_Matches))

count_character_matches <- function(data, character_name) {
    return(nrow(data %>% filter(round_number == 0) %>% filter((Player.1.Character == character_name & Player.2.Character != character_name) |
        (Player.2.Character == character_name & Player.1.Character != character_name))))
}
