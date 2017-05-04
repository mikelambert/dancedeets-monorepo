/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

export type Dancer = {
  id: string,
  name: string,
};

// Currently this is of the form "<timestamp>_<random>"
type SignupKey = string;

export type Signup = {
  id: SignupKey,
  teamName: string,
  dancers: Array<Dancer>,
};

// Various states the competiton can be in,
// this is managed by the Event MC.
type CompetitionState = 'signups' | 'prelims' | 'judged';

export type PrelimStatus = {
  signupKey: SignupKey,
  auditioned: boolean,
};

export type BracketProgress = {
  signupKey: SignupKey,
  // How many wins:
  // 0 means they lost in the first round, or that the first round has not happened yet
  wins: number,
};

type BattleDisplay = {
  // Used for Category display
  name: string,
  // Dance Style named, used for icon lookup
  styleIcon: string,

  styleImageUrl: string,
};

type BattleRules = {
  // The signup requirements, used locally and remotely, to check signups

  // Probably want to turn this off for 1v1s
  needsTeamName: boolean,

  // Usually these will be set to the same value
  teamSize: number,

  // At what point do we cut off new signups
  maxSignupsAllowed: number,

  // How many dancers are we choosing for the top-N?
  bracketSize: number,
};

export type BattleCategory = {
  // Internal id
  id: string,

  display: BattleDisplay,

  rules: BattleRules,
  // This tracks the state of the competition.
  // It also controls the mobile app UI views.
  currentState: CompetitionState,

  // The updating list of pre-registered teams
  // Only modified server-side through the API
  signups: ?{ [signupKey: SignupKey]: Signup },

  // The finalized list of prelims and status,
  // contains keys into the signups object.
  prelims: Array<PrelimStatus>,

  // The finalized list of top-N,
  // contains keys into the signups object,
  // as well as the current status of this team in the bracket.
  bracket: Array<BracketProgress>,
};

export type BattleEvent = {
  // Internal id
  id: string,

  // Public name
  name: string,

  // And image
  headerImageUrl: string,

  categories: { [index: number]: BattleCategory },
};

export function categoryDisplayName(category: BattleCategory) {
  const nxn = category.teamSize
    ? `${category.rules.teamSize}×${category.rules.teamSize}`
    : '';
  const displayName = nxn
    ? `${nxn} ${category.display.name}`
    : category.display.name; // TODO: backup to some variant of 'style'
  return displayName;
}

export function getCategorySignups(category: BattleCategory): Array<Signup> {
  const signups = category.signups;
  if (!signups) {
    return [];
  } else {
    const result: Array<Signup> = Object.keys(signups)
      .sort()
      .map(x => signups[x]);
    return result;
  }
}

export function getCategories(battle: BattleEvent): Array<BattleCategory> {
  const result: Array<BattleCategory> = Object.keys(battle.categories)
    .sort()
    .map(x => battle.categories[x]);
  return result;
}
