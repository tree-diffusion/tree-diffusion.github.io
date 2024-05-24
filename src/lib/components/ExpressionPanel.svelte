<script>
	// Import Skia Canvas-Kit.
	import { onMount } from 'svelte';
	import { loadLang, loadCanvasKit } from '../lang';
	import Spinner from './Spinner.svelte';

	let loading = true;

	export let expression =
		'(- (+ (- (Circle 7 8 8) (Circle 6 8 8)) (Quad 8 8 6 6 H)) (Quad 8 8 A 1 G))';

	export let size = 200;
	let canvas;

	function renderExpression(expression) {
		Promise.all([loadCanvasKit(), loadLang()]).then(([CanvasKit, langLib]) => {
			const ops = langLib.expression_to_ops(expression);

			const objToPath = (obj) => {
				// Split obj by " ".
				const objSplit = obj.split(' ');

				// Obj name is in 0 and numbers are rest.
				const objName = objSplit[0];
				const objNumbers = objSplit.slice(1).map(Number);

				const path = new CanvasKit.Path();
				if (objName === 'circle') {
					// r x y
					path.addCircle(objNumbers[1], objNumbers[2], objNumbers[0]);
					return path;
				} else if (objName === 'quad') {
					path.moveTo(objNumbers[0], objNumbers[1]);
					path.lineTo(objNumbers[2], objNumbers[3]);
					path.lineTo(objNumbers[4], objNumbers[5]);
					path.lineTo(objNumbers[6], objNumbers[7]);
					path.close();
					return path;
				}
			};

			let path = new CanvasKit.Path();
			let pathOp = CanvasKit.PathOp.Union;
			for (const op of ops) {
				if (op === '+') {
					pathOp = CanvasKit.PathOp.Union;
				} else if (op === '-') {
					pathOp = CanvasKit.PathOp.Difference;
				} else {
					path.op(objToPath(op), pathOp);
				}
			}

			// const surface = CanvasKit.MakeCanvasSurface(canvas);
			const surface = CanvasKit.MakeSWCanvasSurface(canvas);
			const surfaceWidth = surface.width();
			const surfaceHeight = surface.height();
			const SCALE_X = surfaceWidth / 32;
			const SCALE_Y = surfaceHeight / 32;

			const background = CanvasKit.parseColorString('#ecf0f1');
			const foreground = CanvasKit.parseColorString('#2d3436');

			const paint = new CanvasKit.Paint();
			paint.setColor(foreground);
			paint.setStyle(CanvasKit.PaintStyle.Fill);
			paint.setAntiAlias(true);
			const rr = CanvasKit.RRectXY(CanvasKit.LTRBRect(10, 60, 210, 260), 25, 15);

			function draw(canvas) {
				canvas.clear(background);
				// Scale the path.
				canvas.scale(SCALE_X, SCALE_Y);
				canvas.drawPath(path, paint);
			}
			surface.drawOnce(draw);
			loading = false;
		});
	}

	// onMount(() => {
	// 	renderExpression(startingExpression);
	// });

	$: renderExpression(expression);
</script>

<div>
	<div
		class="flex justify-center items-center relative"
		style:width={size + 'px'}
		style:height={size + 'px'}
	>
		{#if loading}
			<div class="absolute left-0 right-0 top-0 bottom-0 flex justify-center items-center">
				<Spinner />
			</div>
		{/if}
		<canvas bind:this={canvas} width={size} height={size}></canvas>
	</div>
</div>
