//
//  DanceDeetsUITests.swift
//  DanceDeetsUITests
//
//  Created by LambertMike on 2016/07/22.
//  Copyright © 2016年 Facebook. All rights reserved.
//

import XCTest

class DanceDeetsUITests: XCTestCase {
        
    override func setUp() {
        super.setUp()
        
        // Put setup code here. This method is called before the invocation of each test method in the class.
        
        // In UI tests it is usually best to stop immediately when a failure occurs.
        continueAfterFailure = false
        // UI tests must launch the application that they test. Doing this in setup will make sure it happens for each test method.
        let app = XCUIApplication()
        setupSnapshot(app)
        app.launch()

        // In UI tests it’s important to set the initial state - such as interface orientation - required for your tests before they run. The setUp method is a good place to do this.
    }
    
    override func tearDown() {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
        super.tearDown()
    }
    
    func testExample() {
        // Use recording to get started writing UI tests.
        // Use XCTAssert and related functions to verify your tests produce the correct results.

      
      let app = XCUIApplication()

      NSThread.sleepForTimeInterval(5)

      app.buttons.elementBoundByIndex(0).tap()
      app.buttons.matchingIdentifier("addEvents").element.tap()
      app.buttons.matchingIdentifier("facebookLogin").element.tap()
      //TODO: login

      NSLog("Hey2")
      app.textFields.elementBoundByIndex(0).typeText("nyc")
      NSLog("Hey2")
      snapshot("ListView")

        
    }
    
}
