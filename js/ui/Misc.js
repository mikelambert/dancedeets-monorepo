
import { View } from 'react-native';

export function HorizontalView({style, ...props}: Object): ReactElement {
  return <View style={{flexDirection: 'row'}} {...props} />;
}
