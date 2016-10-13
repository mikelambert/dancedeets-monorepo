/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export type Dancer = {
  uid: String;
  name: String;
};

export type Signup = {
  teamName: string;
  dancers: Array<Dancer>;
};

export type SignupRequirements = {
  needsTeamName: boolean;
  minTeamSize: number;
  maxTeamSize: number;
};

export class CompetitionCategory {
  // Used for Category display
  name: string;
  styleIcon: string; // used for icons
  teamSize: number; // 0 means team size is irrelevant

  signupRequirements: SignupRequirements;
  maxSignupsAllowed: number;
  signups: Array<Signup>;

  constructor(json: any) {
    this.name = json.name;
    this.styleIcon = json.styleIcon;
    this.teamSize = json.teamSize;
    this.signupRequirements = json.signupRequirements;
    this.signups = json.signups;
  }

  displayName() {
    const nxn = this.teamSize ? `${this.teamSize}x${this.teamSize}` : '';
    const displayName = nxn ? `${nxn} ${this.name}` : this.name; //TODO: backup to some variant of 'style'
    return displayName;
  }
}
