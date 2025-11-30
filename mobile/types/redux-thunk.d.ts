declare module 'redux-thunk' {
  import { Action, AnyAction, Middleware, Dispatch as ReduxDispatch } from 'redux';

  export type ThunkAction<
    ReturnType,
    State,
    ExtraThunkArg,
    A extends Action
  > = (
    dispatch: ThunkDispatch<State, ExtraThunkArg, A>,
    getState: () => State,
    extraArgument: ExtraThunkArg
  ) => ReturnType;

  export interface ThunkDispatch<State, ExtraThunkArg, A extends Action> {
    <TReturnType>(
      thunkAction: ThunkAction<TReturnType, State, ExtraThunkArg, A>
    ): TReturnType;
    <TAction extends A>(action: TAction): TAction;
    <TReturnType, TAction extends A>(
      action: TAction | ThunkAction<TReturnType, State, ExtraThunkArg, A>
    ): TAction | TReturnType;
  }

  export type ThunkMiddleware<
    State = Record<string, unknown>,
    BasicAction extends Action = AnyAction,
    ExtraThunkArg = undefined
  > = Middleware<
    ThunkDispatch<State, ExtraThunkArg, BasicAction>,
    State,
    ThunkDispatch<State, ExtraThunkArg, BasicAction>
  >;

  declare const thunk: ThunkMiddleware & {
    withExtraArgument<ExtraThunkArg>(
      extraArgument: ExtraThunkArg
    ): ThunkMiddleware<Record<string, unknown>, AnyAction, ExtraThunkArg>;
  };

  export default thunk;
}
