/**
 * Copyright 2016 DanceDeets.
 */

import jQuery from 'jquery';
import './common';

(globalThis as unknown as { $: typeof jQuery }).$ = jQuery;
(globalThis as unknown as { jQuery: typeof jQuery }).jQuery = jQuery;
