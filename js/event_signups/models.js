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
  // Dance Style named, used for icon lookup
  styleIcon: string;
  // 0 means team size is irrelevant.
  // Non-0 means 1v1 or 2v2
  teamSize: number;

  // The signup requirements, used locally and remotely, to check signups
  signupRequirements: SignupRequirements;
  // At what point do we cut off new signups
  maxSignupsAllowed: number;
  signups: {[key: string]: Signup};
};

export function categoryDisplayName(category: CompetitionCategory) {
  const nxn = category.teamSize ? `${category.teamSize}×${category.teamSize}` : '';
  const displayName = nxn ? `${nxn} ${category.name}` : category.name; //TODO: backup to some variant of 'style'
  return displayName;
}