import React, {Text} from 'react-native';
import { connect } from 'react-redux';
import TutorialScreen from './TutorialScreen';
import { loginComplete } from '../actions';

const mapDispatchToProps = (dispatch) => {
  return {
    onLogin: (event) => {
      dispatch(loginComplete());
    },
  };
};

class OnboardingScreens extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      screen: 'CAROUSEL',
    };
    this._onNoLogin = this._onNoLogin.bind(this);
  }

  _onNoLogin() {
    this.setState({...this.state, screen: 'NO_LOGIN'});
  }

  render() {
    if (this.state.screen === 'CAROUSEL') {
      return <TutorialScreen
        onLogin={this.props.onLogin}
        onNoLogin={this._onNoLogin}
      />;
    } else {
      return <Text>Heeey</Text>;
    }
  }
}

export default connect(
    null,
    mapDispatchToProps
)(OnboardingScreens);
