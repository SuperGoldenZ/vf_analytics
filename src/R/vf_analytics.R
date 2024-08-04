# Load necessary libraries
library(ggplot2)
library(dplyr)
library(scales)
library(tidyr)

# Load the CSV data
data <- read.csv("vf_match_data.csv", row.names=NULL)

frame_to_human_readable_timestamp <- function(frame) {
  total_seconds <- frame / 30
  hours <- floor(total_seconds / 3600)
  minutes <- floor((total_seconds-(hours*3600))/60)
  seconds <- total_seconds %% 60
  
  return(sprintf("%02d:%02d:%05.2f", hours, minutes, seconds))
}

find_fast_rounds <- function (df) {
  rounds <- df%>%
      filter(round_num != 0)
  
  pattern <- "^39\\.|^40\\.|^41\\.|^42\\.|^43\\."
  matching_rows <- grep(pattern, df$round_end_time)
  result_df <- rounds[matching_rows, ]
  cat("Fast ending rounds report\n=========================\n")
  cat(sprintf("%d rounds analyzed\n", nrow(rounds)))
  
  for (i in 1:nrow(result_df)) {
    vid <- result_df$row.names[i]
    frame <- as.integer(result_df$vid[i])
    round_number <- result_df$round_num[i]
    round_end_time <- result_df$round_end_time[i]
    human_readable_timestamp <- frame_to_human_readable_timestamp(frame)
    
    cat(sprintf("https://www.youtube.com/watch?v=%s (Round %d ends in %s at %s)\n", vid, round_number, round_end_time, human_readable_timestamp))
  }
  cat(sprintf("\n%f%% chance of a round ending within six seconds\n\n\n", (nrow(result_df))/(nrow(rounds))*100  ))
}

find_fast_rounds(data)

character_count <- function(data) {
  winning_rounds <- data %>%
    filter(player1_rounds_won == 3 | player2_rounds_won == 3)  %>%
    filter(player1rank >= 21 & player1rank <= 46,
           player2rank >= 21 & player2rank <= 46) 
  
  player1counts = winning_rounds %>% count(player1character, name = "Count")
  player2counts = winning_rounds %>% count(player2character, name = "Count")
  names(player2counts)[names(player2counts) == 'player2character'] <- 'player1character'
  
  combined_df <- bind_rows(player1counts, player2counts) %>%
    group_by(player1character) %>%
    summarise(TotalCount = sum(Count, na.rm = TRUE)) %>%
    ungroup()
  
  results <- combined_df %>%
    arrange(desc(TotalCount))
  
  cat("Character usage report\n=========================\n")
  for (i in 1:nrow(results)) {
    cat(sprintf("%s,%d\n", results$player1character[i], results$TotalCount[i]))
  }
}

stage_count <- function(data) {
  winning_rounds <- data %>%
    filter(player1_rounds_won == 3 | player2_rounds_won == 3)
  
  stage_counts = winning_rounds %>% count(stage, name = "Count")
  
  stage_counts$stage <- factor(stage_counts$stage, levels = stage_counts$stage[order(stage_counts$Count, decreasing = TRUE)])  
  
  ggplot(stage_counts, aes(x = stage, y = Count)) +
    geom_bar(stat = "identity") +
    xlab("Name") +
    ylab("Count") +
    ggtitle(paste("VF5es",nrow(winning_rounds),"match sample")) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
}

rank_winrate_distribution <- function(data){
  cat("\n\nWin probability table\n")
  cat("=========================\n")
  winning_rounds <- data %>%
    filter(player1_rounds_won == 3 | player2_rounds_won == 3)  %>%
    filter(player1rank >= 21 & player1rank <= 46,
           player2rank >= 21 & player2rank <= 46) 
  
  matches_combined <- winning_rounds %>%
    mutate(combination1 = paste(player1rank, player2rank, sep = " vs "),
           combination2 = paste(player2rank, player1rank, sep = " vs ")) %>%
    select(combination1, combination2) %>%
    pivot_longer(cols = everything(), names_to = "combination_type", values_to = "rank_combination") %>%
    select(rank_combination)  
  
  match_counts <- matches_combined %>%
    separate(rank_combination, into = c("player1_rank", "player2_rank"), sep = " vs ", convert = TRUE) %>%
    count(player1_rank, player2_rank, name = "match_count") %>%
    complete(player1_rank = sort(unique(c(winning_rounds$player1_rank, winning_rounds$player2_rank))),
             player2_rank = sort(unique(c(winning_rounds$player1_rank, winning_rounds$player2_rank))),
             fill = list(match_count = 0))
  
  # Spread the data to create a matrix-like table
  match_table <- match_counts %>%
    spread(key = player2_rank, value = match_count)
  
  # Print the table
  #print(match_table, n=46)  
  
  rank_range <- 21:46
  win_counts <- matrix(0, nrow = length(rank_range), ncol = length(rank_range), 
                       dimnames = list(rank_range, rank_range))
  
  for (i in 1:nrow(winning_rounds)) {
    p1_rank <- winning_rounds$player1rank[i]
    p2_rank <- winning_rounds$player2rank[i]
    p1_wins <- winning_rounds$player1_rounds_won[i]
    p2_wins <- winning_rounds$player2_rounds_won[i]
    
    if (p1_wins == 3) {
      win_counts[as.character(p1_rank), as.character(p2_rank)] <- win_counts[as.character(p1_rank), as.character(p2_rank)] + 1
    } else if (p2_wins == 3) {
      win_counts[as.character(p2_rank), as.character(p1_rank)] <- win_counts[as.character(p2_rank), as.character(p1_rank)] + 1
    }
  }
  
  #Remove where we don't have much data
  win_counts[ win_counts < 25 ] <- 0
  
  win_percentages <- matrix(NA, nrow = length(rank_range), ncol = length(rank_range), 
                            dimnames = list(rank_range, rank_range))
  formatted_win_percentages <- matrix("", nrow = length(rank_range), ncol = length(rank_range), 
                                      dimnames = list(rank_range, rank_range))
  # Calculate win percentages
  for (i in 1:length(rank_range)) {
    for (j in 1:length(rank_range)) {
      total_matches <- win_counts[i, j] + win_counts[j, i]
      if (total_matches > 0) {
        win_percentages[i, j] <- paste(round(win_counts[i, j] / total_matches * 100),"%", sep="")
        #formatted_win_percentages[i, j] <- paste0(win_percentages, "%")
      }
    }
  }
  
  win_percentages[is.na(win_percentages)] <- ""
  win_percentages[win_percentages=="100%"]<-""
  win_percentages[win_percentages=="0%"]<-""
  print(noquote(win_percentages))
}

character_count(data)
stage_count(data)
rank_winrate_distribution(data)
quit(save="no")
# Convert match_end_time to numeric, converting non-numeric values to NA
#data$match_end_time <- as.numeric(as.character(data$match_end_time))

# Filter out rows with match_end_time equal to 45.00 and remove NA values
sorted_df <- data[order(data$round_end_time), ]

# Display the rows with the highest numeric values
print(sorted_df)

print(unique(data['stage']))
nrow(data)
unique(data$player1character)
unique(data$player1ringname)
unique(data$stage)
mean(data$player1rank)

character_matchup_distribution <- function(data){
  winning_rounds <- data %>%
    filter(player1_rounds_won == 3 | player2_rounds_won == 3)  %>%
    filter(player1rank >= 21 & player1rank <= 46,
           player2rank >= 21 & player2rank <= 46) 
  
  matches_combined <- winning_rounds %>%
    mutate(combination1 = paste(player1character, player2character, sep = " vs "),
           combination2 = paste(player2character, player1character, sep = " vs ")) %>%
    select(combination1, combination2) %>%
    pivot_longer(cols = everything(), names_to = "combination_type", values_to = "character_combination") %>%
    select(character_combination)  

  print(matches_combined)  
  
  match_counts <- matches_combined %>%
    separate(character_combination, into = c("player1_character", "player2_character"), sep = " vs ") %>%
    count(player1_character, player2_character) %>%
    complete(player1_character = sort(unique(c(winning_rounds$player1character, winning_rounds$player2character))),
             player2_character = sort(unique(c(winning_rounds$player1character, winning_rounds$player2character))),
             fill = list(n = 0))  
  
  # Spread the data to create a matrix-like table
  match_table <- match_counts %>%
    spread(key = player2_character, value = n)
  
  # Print the table
  print(match_table)  
  
}

character_matchup_distribution(data)


rank_winrate_distribution(data)

rank_distribution <- function(data) {
  winning_rounds <- data %>%
    filter(player1_rounds_won == 3 | player2_rounds_won == 3)  %>%
    filter(player1rank >= 21 & player1rank <= 46,
           player2rank >= 21 & player2rank <= 46)
  
  match_counts <- winning_rounds %>%
    count(player1rank, player2rank) %>%
    complete(player1rank = 21:46, player2rank = 21:46, fill = list(n = 0))  
  
  match_table <- match_counts %>%
    spread(key = player2rank, value = n)
  
  print(noquote(match_table), n=46)
  }

  rank_distribution(data)

format_winning_rounds <- function(data) {
  winning_rounds <- data %>%
    filter(player1_rounds_won == 3 | player2_rounds_won == 3)  
  
  winning_rounds <- winning_rounds %>%
    filter(player1rank != 0 & player2rank != 0)  
  
  # Calculate the difference in ranks between player 1 and player 2
  data <- winning_rounds %>%
    mutate(player1_rank_difference = player1rank - player2rank)
  
  data <- data %>%
    mutate(player2_rank_difference = player2rank - player1rank)

  large_gaps <- data %>%
      filter (abs(player1_rank_difference) > 30)   
  #print(data %>% filter (abs(player1_rank_difference) > 10))
  
  # Determine the winner for each match
  data <- data %>%
    mutate(player_1_wins = ifelse(player1_rounds_won >= 3, 1, 0),
           player_2_wins = ifelse(player2_rounds_won >= 3, 1, 0))
  
  # Ensure only one player wins per match
  data <- data %>%
    mutate(winner = ifelse(player_1_wins == 1, "Player 1", ifelse(player_2_wins == 1, "Player 2", "n/a")))

  print("Num samples")
  nrow(data)
  print(paste("Sample size ", nrow(data)))  
  #player1_blaze_matches <- data %>%
    #filter(player1character == "Blaze" & player1character != player2character)
  
  #player2_blaze_matches <- data %>%
    #filter(player2character == "Blaze" & player1character != player2character)
  
  #blaze_sample_size = nrow(player1_blaze_matches)   + nrow(player2_blaze_matches)
  
  #player1 blaze change to data for original
  player1_win_data <- data %>%
    mutate(rank_difference = player1_rank_difference)
  
  player1_win_data <- player1_win_data %>%
    group_by(rank_difference) %>%
    summarize(win_percentage = mean(winner == "Player 1") * 100)
  
  #player2_win_data <- data %>%
  player2_win_data <- data %>%
    mutate(rank_difference = player2_rank_difference)
  
  player2_win_data <- player2_win_data %>%
    group_by(rank_difference) %>%
    summarize(win_percentage = mean(winner == "Player 2") * 100)
  
  appended_data = bind_rows(player1_win_data, player2_win_data) %>%
    filter(win_percentage != 0 & win_percentage != 100)
  
  return (bind_rows(player1_win_data, player2_win_data))
}

plot_both_players <- function(data, character) {
  if (!missing(character)) {
    data <- data %>%
      filter(player1character == character | player2character == character)
  
    data <- data %>%
      filter(player1character != player2character)
  }
  
  data <- format_winning_rounds(data)
  data <- data %>%
    filter(win_percentage != 0 & win_percentage != 100)
  
  data <- data %>%
    filter(abs(rank_difference) <= 20)
    
  model <- lm(formula = win_percentage ~ rank_difference, data = data)
  
  rank_difference <- c(-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6)
  win_percentage <- c(0)
  
  df <- data.frame(rank_difference = rank_difference, win_percentage = win_percentage)
  predict(model, df)
  
  summary(model)
  
  
    #print(data)  
  #print(nrow(data))
  ggplot() +
    # First dataset
    geom_point(data = data, aes(x = rank_difference, y = win_percentage), color = "blue") +
    geom_smooth(data = data, aes(x = rank_difference, y = win_percentage), method = "lm", col = "blue") +
    
    # Second dataset
    #geom_point(data = first_round_winners, aes(x = rank_difference, y = win_percentage), color = "purple") +
    #geom_smooth(data = another_data, aes(x = rank_difference, y = win_percentage), method = "lm", col = "purple") +
    
    # Common scales and labels
    scale_y_continuous(labels = percent_format(scale = 1), limits = c(0, 100)) +
    labs(title = paste("Winning Percentage By Rank Difference (", nrow(data), " samples)"),
         x = "Rank Difference ランク差",
         y = "Win Percentage 勝率") +
    theme_minimal()
  
  
  #ggplot(appended_data, aes(x = rank_difference, y = win_percentage)) +
    #geom_point() +
    #geom_smooth(method = "lm", col = "blue") +
    #scale_y_continuous(labels = percent_format(scale = 1), limits = c(0, 100)) +
    #labs(title = paste("Winning Percentage By Rank Difference (", sample_size , " samples)"),
         #x = "Rank Difference ランク差",
         #y = "Win Percentage 勝率") +
    #theme_minimal()
  
}

plot_both_players(data)


print(winning_rounds)
print(nrow(winning_rounds))



print(data)

# Remove rows where the winner is "N/A"
data <- data %>%
  filter(winner != "n/a")


# Calculate win percentage for player 1based on rank difference


print(nrow(player1_win_data))
print(nrow(player2_win_data))
print(nrow(appended_data))



ggplot(player1_win_data, aes(x = player1_rank_difference, y = player_1_win_percentage)) +
  geom_point() +
  geom_smooth(method = "lm", col = "blue") +
  scale_y_continuous(labels = percent_format(scale = 1), limits = c(0, 100)) +
  labs(title = "Winning Percentage By Rank Difference",
       x = "Rank Difference",
       y = "Win Percentage") +
  theme_minimal()

ggplot(player2_win_data, aes(x = player2_rank_difference, y = player_2_win_percentage)) +
  geom_point() +
  geom_smooth(method = "lm", col = "blue") +
  scale_y_continuous(labels = percent_format(scale = 1), limits = c(0, 100)) +
  labs(title = "Winning Percentage By Rank Difference",
       x = "Rank Difference",
       y = "Win Percentage") +
  theme_minimal()

# Summarize the data by match_id to get the winner of each match
match_results <- data %>%
  summarize(rank_difference = first(rank_difference),
            player_1_wins = max(player_1_wins),
            player_2_wins = max(player_2_wins),
            winner = ifelse(max(player_1_wins) == 1, "Player 1",
                            ifelse(max(player_2_wins) == 1, "Player 2", "N/A")))

# Remove rows where the winner is "N/A"
match_results <- match_results %>%
  filter(winner != "N/A")

# Filter the data to include only matches where the higher-ranked player won
higher_rank_wins <- match_results %>%
  filter((rank_difference > 0 & winner == "Player 1") | (rank_difference < 0 & winner == "Player 2"))

lower_rank_wins <- match_results %>%
  filter((rank_difference < 0 & winner == "Player 1") | (rank_difference > 0 & winner == "Player 2"))

# Count the number of such matches
num_higher_rank_wins <- nrow(higher_rank_wins)

print(nrow(match_results))
# Print the result
print(num_higher_rank_wins)
print(nrow(lower_rank_wins))



# Summarize the data by match_id to get the winner of each match
match_results <- data %>%
  group_by(match_id) %>%
  summarize(rank_difference = first(rank_difference),
            player_1_wins = max(player_1_wins),
            player_2_wins = max(player_2_wins),
            winner = ifelse(max(player_1_wins) == 1, "Player 1",
                            ifelse(max(player_2_wins) == 1, "Player 2", "N/A")))

big_gaps <- function (data) {
  gaps = data %>% filter (abs(player1rank - player2rank) > 5)
  return(unique(gaps[c('vid', 'player1rank', 'player2rank', 'player1ringname', 'player2ringname', 'player1character', 'player2character')]))
}

gaps <- big_gaps(data)


# Remove rows where the winner is "N/A"
match_results <- match_results %>%
  filter(winner != "N/A")

# Filter the data to include only matches where the higher-ranked player won
higher_rank_wins <- match_results %>%
  filter((rank_difference > 0 & winner == "Player 1") | (rank_difference < 0 & winner == "Player 2"))

lower_rank_wins <- match_results %>%
  filter((rank_difference < 0 & winner == "Player 1") | (rank_difference > 0 & winner == "Player 2"))

same_rank <- match_results %>%
  filter((rank_difference == 0 & winner == "Player 1") | (rank_difference == 0 & winner == "Player 2"))

# Count the number of such matches
num_higher_rank_wins <- nrow(higher_rank_wins)

# Print the result
print(nrow(same_rank))
print(num_higher_rank_wins)
print(nrow(lower_rank_wins))

print(higher_rank_wins)

write.table(unique(gaps['vid']), "gaps.txt", row.names = FALSE)
#fileConn<-file("gaps.txt")
#writeLines(gaps, fileConn)
#close(fileConn)