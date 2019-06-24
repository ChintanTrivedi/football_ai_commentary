class Commentary:
    def __init__(self):
        # match info
        self.current_game_mode = None
        self.all_game_modes = ['game_mode_normal', 'game_mode_kickoff', 'game_mode_goalkick', 'game_mode_freekick',
                               'game_mode_corner', 'game_mode_throwin', 'game_mode_penalty']
        self.first_kickoff = True
        self.home_score = 0
        self.away_score = 0
        self.possession_team = -1
        self.home_team_yellow_cards = 0
        self.away_team_yellow_cards = 0

    def process_observation(self, observation):
        # input to model
        prompt = ''

        # interrupt current speech for important eents like goal
        interrupt_current_commentary = False

        # game mode information
        game_mode = observation['game_mode']
        if self.current_game_mode != game_mode:
            self.current_game_mode = game_mode
            print(self.all_game_modes[self.current_game_mode])
            if self.first_kickoff:
                self.first_kickoff = False
                interrupt_current_commentary = True
                prompt = 'The football match is starting from the first minute with a kickoff of the ball. '
            elif self.current_game_mode == 1:  # kickoff
                print('todo: kickoff')
                # prompt = 'And we start again with the kickoff'
            elif self.current_game_mode == 2:  # goal kick
                print('todo: goalkick')
                # prompt = 'After all that build up from the attacking team, it will only be a goal kick'
            elif self.current_game_mode == 3:  # free kick
                prompt = '﻿That\'s a free kick. '
            elif self.current_game_mode == 4:  # corner
                print('todo: corner')
                # prompt = 'The ball goes behind for a corner'
            elif self.current_game_mode == 5:  # throw in
                print('todo: throwin')
                # prompt = 'The ball goes out for a throw in'
            elif self.current_game_mode == 6:  # penalty
                print('todo: penalty')
                # prompt = 'Oh dear the ref has given a penalty he is pointing to the spot'
        elif self.current_game_mode == 0:
            # normal mode - no major events happening - time to talk about filler details
            if observation['ball_owned_team'] != self.possession_team:
                self.possession_team = observation['ball_owned_team']
                print('todo: filler talk')
                # prompt = 'The ball changes possession '

        # card/booking information
        total_home_cards = sum(observation['home_team_yellow_card'])
        total_away_cards = sum(observation['away_team_yellow_card'])
        if total_home_cards > self.home_team_yellow_cards:
            self.home_team_yellow_cards = total_home_cards
            interrupt_current_commentary = True
            prompt = 'That will be a yellow card for the home side'
        if total_away_cards > self.away_team_yellow_cards:
            self.away_team_yellow_cards = total_away_cards
            interrupt_current_commentary = True
            prompt = 'That will be a booking for the away side'

        # goal information
        score = observation['score']
        if score[0] > self.home_score:
            self.home_score = score[0]
            interrupt_current_commentary = True
            prompt = 'And that\'s a goal for this home side! '
        if score[1] > self.away_score:
            self.away_score = score[1]
            interrupt_current_commentary = True
            prompt = 'And that\'s a goal for this away side! '

        return prompt, interrupt_current_commentary
