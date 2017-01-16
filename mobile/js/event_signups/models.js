/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

export type Dancer = {
  name: String;
};

export type Signup = {
  teamName: string;
  dancers: ?{[uid: string]: Dancer};
};

export type SignupRequirements = {
  needsTeamName: boolean;
  minTeamSize: number;
  maxTeamSize: number;
};

// Currently this is of the form "<timestamp>_<random>"
type SignupKey = string;

// Various states the competiton can be in,
// this is managed by the Event MC.
type CompetitionState = 'signups' | 'prelims' | 'judged';

export type PrelimStatus = {
  signupKey: SignupKey;
  auditioned: boolean;
};

export type BracketProgress = {
  signupKey: SignupKey;
  // How many wins:
  // 0 means they lost in the first round, or that the first round has not happened yet
  wins: number;
};

export type CompetitionCategory = {
  // Used for modifications through the server API
  id: string;

  // Display Info:
  // Used for Category display
  name: string;
  // Dance Style named, used for icon lookup
  styleIcon: string;
  // 0 means team size is irrelevant.
  // Non-0 means 1v1 or 2v2
  teamSize: number;

  // Event Logic Info:
  // The signup requirements, used locally and remotely, to check signups
  signupRequirements: SignupRequirements;
  // At what point do we cut off new signups
  maxSignupsAllowed: number;
  // How many dancers are we choosing for the top-N?
  bracketSize: number;

  // This tracks the state of the competition.
  // It also controls the mobile app UI views.
  currentState: CompetitionState;

  // The updating list of pre-registered teams
  // Only modified server-side through the API
  signups: ?{[signupKey: SignupKey]: Signup};

  // The finalized list of prelims and status,
  // contains keys into the signups object.
  prelims: Array<PrelimStatus>;

  // The finalized list of top-N,
  // contains keys into the signups object,
  // as well as the current status of this team in the bracket.
  bracket: Array<BracketProgress>;
};

export type BattleEvent = {
  name: string;
  headerImageUrl: string;

  categories: Array<CompetitionCategory>;
};

export function categoryDisplayName(category: CompetitionCategory) {
  const nxn = category.teamSize ? `${category.teamSize}×${category.teamSize}` : '';
  const displayName = nxn ? `${nxn} ${category.name}` : category.name; // TODO: backup to some variant of 'style'
  return displayName;
}
