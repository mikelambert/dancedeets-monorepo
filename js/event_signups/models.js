/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export type Dancer = {
  name: String;
};

export type Signup = {
  teamName: string;
  dancers: {[uid: string]: Dancer};
};

export type SignupRequirements = {
  needsTeamName: boolean;
  minTeamSize: number;
  maxTeamSize: number;
};

export type CompetitionCategory = {
  // Used for Category display
  name: string;
  styleIcon: string; // used for icons
  teamSize: number; // 0 means team size is irrelevant

  signupRequirements: SignupRequirements;
  maxSignupsAllowed: number;
  signups: Array<Signup>;
};

export function categoryDisplayName(category: CompetitionCategory) {
  const nxn = category.teamSize ? `${category.teamSize}×${category.teamSize}` : '';
  const displayName = nxn ? `${nxn} ${category.name}` : category.name; //TODO: backup to some variant of 'style'
  return displayName;
}