import * as React from 'react';
import { Animated, Easing, StyleProp, View, ViewStyle } from 'react-native';

const ANIMATED_EASING_PREFIXES = ['easeInOut', 'easeOut', 'easeIn'];

interface Props {
  align: 'top' | 'center' | 'bottom';
  collapsed: boolean;
  collapsedHeight: number;
  duration: number;
  easing: string | ((value: number) => number);
  style?: StyleProp<ViewStyle>;
  children: React.ReactNode;
}

interface State {
  measuring: boolean;
  measured: boolean;
  height: Animated.Value;
  contentHeight: number;
  animating: boolean;
}

class Collapsible extends React.Component<Props, State> {
  static defaultProps: Partial<Props> = {
    align: 'top',
    collapsed: true,
    collapsedHeight: 0,
    duration: 300,
    easing: 'easeOutCubic',
  };

  _handleRef = (ref: any) => {
    this.contentHandle = ref;
  };

  _animation?: Animated.CompositeAnimation;
  contentHandle: any = null;

  _measureContent(callback: (height: number) => void) {
    this.setState(
      {
        measuring: true,
      },
      () => {
        requestAnimationFrame(() => {
          if (!this.contentHandle) {
            this.setState(
              {
                measuring: false,
              },
              () => callback(this.props.collapsedHeight)
            );
          } else {
            this.contentHandle.getNode().measure((x: number, y: number, width: number, height: number) => {
              this.setState(
                {
                  measuring: false,
                  measured: true,
                  contentHeight: height,
                },
                () => callback(height)
              );
            });
          }
        });
      }
    );
  }

  _toggleCollapsed(collapsed: boolean) {
    if (collapsed) {
      this._transitionToHeight(this.props.collapsedHeight);
    } else if (!this.contentHandle) {
      if (this.state.measured) {
        this._transitionToHeight(this.state.contentHeight);
      }
    } else {
      this._measureContent((contentHeight: number) => {
        this._transitionToHeight(contentHeight);
      });
    }
  }

  _transitionToHeight(height: number) {
    const { duration } = this.props;
    let easing: any = this.props.easing;
    if (typeof easing === 'string') {
      let prefix: string;
      let found = false;
      for (let i = 0; i < ANIMATED_EASING_PREFIXES.length; i += 1) {
        prefix = ANIMATED_EASING_PREFIXES[i];
        if (easing.substr(0, prefix.length) === prefix) {
          easing =
            easing.substr(prefix.length, 1).toLowerCase() +
            easing.substr(prefix.length + 1);
          prefix = prefix.substr(4, 1).toLowerCase() + prefix.substr(5);
          easing = (Easing as any)[prefix]((Easing as any)[easing || 'ease']);
          found = true;
          break;
        }
      }
      if (!found) {
        easing = (Easing as any)[easing];
      }
      if (!easing) {
        throw new Error(`Invalid easing type "${String(this.props.easing)}"`);
      }
    }

    if (this._animation) {
      this._animation.stop();
    }
    this.setState({ animating: true });
    this._animation = Animated.timing(this.state.height, {
      toValue: height,
      duration,
      easing,
      useNativeDriver: true,
    });
    this._animation.start(event => this.setState({ animating: false }));
  }

  _handleLayoutChange = (event: any) => {
    const contentHeight = event.nativeEvent.layout.height;
    if (
      this.state.animating ||
      this.props.collapsed ||
      this.state.measuring ||
      this.state.contentHeight === contentHeight
    ) {
      return;
    }
    this.state.height.setValue(contentHeight);
    this.setState({ contentHeight });
  };

  constructor(props: Props) {
    super(props);
    this.state = {
      measuring: false,
      measured: false,
      height: new Animated.Value(props.collapsedHeight),
      contentHeight: 0,
      animating: false,
    };
  }

  componentDidUpdate(prevProps: Props) {
    if (prevProps.collapsed !== this.props.collapsed) {
      this._toggleCollapsed(this.props.collapsed);
    } else if (
      this.props.collapsed &&
      prevProps.collapsedHeight !== this.props.collapsedHeight
    ) {
      this.state.height.setValue(this.props.collapsedHeight);
    }
  }

  render() {
    const { collapsed } = this.props;
    const { height, contentHeight, measuring, measured } = this.state;
    const hasKnownHeight = !measuring && (measured || collapsed);
    const style: any = hasKnownHeight && {
      overflow: 'hidden',
      height: collapsed ? 0 : contentHeight,
    };
    const contentStyle: any = {};
    if (measuring) {
      contentStyle.position = 'absolute';
      contentStyle.opacity = 0;
    } else if (this.props.align === 'center') {
      contentStyle.transform = [
        {
          translateY: height.interpolate({
            inputRange: [0, contentHeight],
            outputRange: [contentHeight / -2, 0],
          }),
        },
      ];
    } else if (this.props.align === 'bottom') {
      contentStyle.transform = [
        {
          translateY: height.interpolate({
            inputRange: [0, contentHeight],
            outputRange: [-contentHeight, 0],
          }),
        },
      ];
    }
    return (
      <View style={style} pointerEvents={collapsed ? 'none' : 'auto'}>
        <Animated.View
          ref={this._handleRef}
          style={[this.props.style, contentStyle]}
          onLayout={this.state.animating ? undefined : this._handleLayoutChange}
        >
          {this.props.children}
        </Animated.View>
      </View>
    );
  }
}

export default Collapsible;
