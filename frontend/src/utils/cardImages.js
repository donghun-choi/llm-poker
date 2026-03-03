export default function cardImage(card) {
  if (typeof card === 'number') {
    return '/cards/back.svg';
  }
  const name = String(card).toUpperCase();
  return `/cards/${name}.svg`;
}
