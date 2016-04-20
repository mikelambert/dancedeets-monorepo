import React, {Text} from 'react-native';
import { connect } from 'react-redux';
import TutorialScreen from './TutorialScreen';
import { loginComplete, loginTutorialNoLogin, loginTutorialStillNoLogin } from '../actions';

const mapStateToProps = (state) => {
  return {
    onboarding: state.onboarding,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onLogin: (event) => {
      dispatch(loginComplete());
    },
    onNoLogin: (event) => {
      dispatch(loginTutorialNoLogin());
    },
    onStillNoLogin: (event) => {
      dispatch(loginTutorialStillNoLogin());
    },
  };
};

class OnboardingScreens extends React.Component {
  render() {
    console.log(this.props);
    if (this.props.onboarding.type === 'CAROUSEL') {
      return <TutorialScreen
        onLogin={this.props.onLogin}
        onNoLogin={this.props.onNoLogin}
      />;
    } else {
      return <Text>Heeey</Text>;
    }
  }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(OnboardingScreens);
