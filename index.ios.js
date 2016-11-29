import { AppRegistry } from 'react-native';
import setup from './js/app/setup';
import trackErrors from './js/trackerrors';

AppRegistry.registerComponent('DanceDeets', setup);
trackErrors();
