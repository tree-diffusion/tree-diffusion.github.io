<script>
	import ExpressionCodeInner from './ExpressionCodeInner.svelte';
	import { loadLang } from '../lang';

	export let expression =
		'(- (+ (- (Circle 7 8 8) (Circle 6 8 8)) (Quad 8 8 6 6 H)) (Quad 8 8 A 1 G))';

	let parsed = null;

	const parseExpression = (expression) => {
		loadLang().then((lib) => {
			parsed = lib.parse_expression(expression);
		});
	};

	$: parseExpression(expression);
</script>

<ExpressionCodeInner data={parsed} />
